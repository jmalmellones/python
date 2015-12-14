import time
import json
import sys
import re
from time import mktime
from datetime import datetime

import feedparser
import pymongo
import logging

import download_file
from synology_client import General, DownloadStation, FileStation
import say
import prowl_notifier
import quitar_elitetorrent
import os.path

__author__ = 'jmalmellones'

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger('rss_downloader')

config_file = 'rss_downloader.json'
config = json.load(open(config_file))


def reload_config():
    return json.load(open(config_file))


def download_dir():
    return config['download_dir']


def session_name():
    return config['session_name']


def notify_using_prowl(event, description):
    """
    convenience method to call prowl with a notification
    """
    prowl_notifier.send_notification('rss_downloader', event, description)


def notify_using_tts(event, description):
    """
    convenience method to notify with tts
    """
    say.say(event + ", " + description)


def from_datetime_struct_to_timestamp(date_time_struct):
    """
    it is supposed to convert time returned from feedparser to datetime.datetime
    """
    return datetime.fromtimestamp(mktime(date_time_struct))


def included(title):
    """ returns True if title is included in the configuration """
    for include in includes:
        if include['cadena'].lower() in title.lower():
            print title.lower(), ' matches ', include['cadena'].lower()
            return True
    return False


def excluded(title):
    """ returns True if title is excluded in the configuration """
    for exclude in excludes:
        if exclude.lower() in title.lower():
            print title.lower(), ' excluded by filter ', exclude.lower()
            return True
    return False


def treat_entry(entry, security_id, torrents):
    """
    treats each of the rss entries
    """
    esperar = False
    titulo = entry['title_detail']['value']
    url = entry['link']
    fecha = entry['published_parsed']
    documento = {"titulo": titulo, "url": url, "fecha": from_datetime_struct_to_timestamp(fecha)}
    document = torrents.find_one(documento)
    if document:
        print "'", titulo, "' already processed, skipping"
    else:
        is_included = included(titulo)
        is_excluded = excluded(titulo)
        documento['incluido'] = is_included
        documento['excluido'] = is_excluded
        if is_excluded:
            print "filter discards '", titulo, "'"
        else:
            if is_included:
                print "downloading ", titulo, " at url ", url
                html = download_file.download_url_html(url)
                esperar = True
                magnets = download_file.download_magnet_in_html_regex(html)
                for magnet in magnets:
                    DownloadStation.add_task(magnet, security_id)
                documento['descargado'] = True
            else:
                print "filter does not include '", titulo, "'"
                notify_using_prowl(titulo + " not included", url)  # lets you download it manually
                documento['notificado'] = True
        torrents.insert(documento)
    if esperar:
        print "waiting 10 seg..."
        time.sleep(10)  # wait 10 seconds trying not to trigger server DOS counter measures


def get_mongo_client():
    connection = pymongo.MongoClient(config['mongodb']['host'], config['mongodb']['port'])
    return connection


def reload_includes():
    result = []
    connection = get_mongo_client()
    the_includes = connection.descargas.includes.find()
    for include in the_includes:
        result.append({'cadena': include['cadena'], 'destino': include['destino']})
    connection.close()
    return result

includes = reload_includes()

def reload_excludes():
    result = []
    connection = get_mongo_client()
    the_excludes = connection.descargas.excludes.find()
    for exclude in the_excludes:
        result.append(exclude['cadena'])
    connection.close()
    return result

excludes = reload_excludes()


def read_elitetorrent():
    print "reading data from elitetorrent"
    d = feedparser.parse('http://www.elitetorrent.net/rss.php')
    if d['status'] == 200:
        print('status ok, interpreting data')
        connection = get_mongo_client()
        torrents = connection.descargas.torrents
        # respuestas_rss = connection.descargas.respuestas_rss
        security_id = General.login(session_name())
        for theEntry in d['entries']:
            treat_entry(theEntry, security_id, torrents)
        connection.close()
        General.logout(session_name())
    else:
        print("status received from server is not 200, giving up...")


def download_previously_not_included():
    print "searching included that previously were skipped"
    connection = get_mongo_client()
    security_id = General.login(session_name())
    torrents = connection.descargas.torrents
    for include in includes:
        print "checking include ", include['cadena'], " to see if we left something..."
        documento = {"titulo": re.compile(include['cadena'], re.IGNORECASE), "incluido": False, "excluido": False}
        for doc in torrents.find(documento):
            # vemos si por el titulo exacto ya se ha descargado
            titulo = doc['titulo']
            url = doc['url']
            encontrado = torrents.find_one({'titulo': titulo})
            if "descargado" not in encontrado or encontrado['descargado'] is False:
                print "downloading ", titulo, " at url ", url
                html = download_file.download_url_html(url)
                magnets = download_file.download_magnet_in_html_regex(html)
                for magnet in magnets:
                    DownloadStation.add_task(magnet, security_id)
                encontrado['descargado'] = True
                encontrado['incluido'] = True
                torrents.save(encontrado)
                print "updated document to remember that it was already downloaded"
                print "waiting 10 seg..."
                time.sleep(10)  # wait 10 seconds trying not to trigger server DDOS counter measures
    General.logout(session_name())
    connection.close()


def move_finished_to_destination():
    print "moving finished tasks to destination folder"
    security_id = General.login(session_name())
    tasks = DownloadStation.get_tasks(security_id)
    # for each task in download station
    for task in tasks['data']['tasks']:
        # where task has ended seeding
        if task['status'] == 'finished':
            title = task['title']
            id = task['id']
            for include in includes:
                # if the task was included automatically
                if include['cadena'].lower() in title.lower():
                    # we check if destination folder exists
                    info = FileStation.get_info(include['destino'], security_id)
                    if info['success']:
                        destino = info['data']['files'][0]
                        if 'code' in destino and destino['code'] == 408:
                            print "the directory does not exist, we create it"
                            norm = os.path.normpath(destino['path'])
                            nombre = os.path.basename(norm)
                            path = os.path.dirname(norm)
                            FileStation.create_folder(path, nombre, security_id)
                        fichero_a_mover = download_dir() + '/' + title
                        if FileStation.move(fichero_a_mover, destino['path'], security_id):
                            print "moved ", fichero_a_mover, " to ", destino['path'], ", eliminando tarea"
                            if DownloadStation.delete_task(id, security_id):
                                print "deleted task ", id
                            say.say("ya esta disponible el fichero " + title + " en el NAS")
                        else:
                            print "hubo un problema moviendo fichero ", title
                    else:
                        print "error obtaining info about ", include['destino']
    General.logout(session_name())


if __name__ == "__main__":
    try:
        while True:
            try:
                say.say("voy a mover los torrent terminados al directorio de videos")
                move_finished_to_destination()
            except TypeError as e:
                print e
            except:
                errorMoving = "Unexpected error moving finished tasks to destination"
                log.exception(errorMoving)
                print errorMoving, ":", sys.exc_info()
                notify_using_prowl(errorMoving, str(sys.exc_info()))

            try:
                say.say("estoy quitando la marca elite torrent a todos los ficheros de pelis y series")
                quitar_elitetorrent.quitar_elitetorrent()
            except:
                print "Unexpected error removing elitetorrent from files' names:", sys.exc_info()
                notify_using_prowl("Unexpected error emoving elitetorrent from files' names", str(sys.exc_info()))

            try:
                say.say("estoy repasando por si me he dejado algo por bajar")
                download_previously_not_included()
            except:
                print "Unexpected error downloading previously not included tasks:", sys.exc_info()
                notify_using_prowl("Unexpected error downloading previously not included", str(sys.exc_info()))
            try:
                say.say("contactando con elitetorrent, viendo si hay algo nuevo")
                read_elitetorrent()
            except:
                print "Unexpected error reading elitetorrent:", sys.exc_info()
                notify_using_prowl("Unexpected error reading elitetorrent", str(sys.exc_info()))
            say.say("hasta dentro de 2 horas!")
            print("waiting 2 hours to ask again...")
            time.sleep(60 * 60 * 2)  # 1 hour
            config = reload_config()
            includes = reload_includes()
            excludes = reload_excludes()
    except KeyboardInterrupt:
        print "finishing..."
        sys.exit()