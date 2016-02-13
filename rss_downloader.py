"""
    RSS Downloader. Automatically download rss linked pages' torrents.
    Copyright (C) 2016 Jose Miguel Almellones Cabello

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import time
import json
import sys
import re
from time import mktime
from datetime import datetime
import os.path
import traceback

import feedparser
import pymongo
import logging

import download_file
from synology_client import General, DownloadStation, FileStation
import say
# import prowl_notifier
import telegram_bot
import quitar_elitetorrent
import unicode_functions

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


def notify_mobile_phone(event, description):
    """
    convenience method to call prowl with a notification
    """
    #prowl_notifier.send_notification('rss_downloader', event, description)
    telegram_bot.sendMessage(event + ' ' + description)


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
            #TODO: print this with unicode functions
            #print title.lower(), ' matches ', include['cadena'].lower()
            return True
    return False


def excluded(title):
    """ returns True if title is excluded in the configuration """
    for exclude in excludes:
        if exclude.lower() in title.lower():
            #TODO: print this with unicode functions
            #print title.lower(), ' excluded by filter ', exclude.lower()
            return True
    return False


def treat_entry(entry, security_id, torrents):
    """ treats each of the rss entries """
    esperar = False
    titulo = entry['title_detail']['value']
    url = entry['link']
    fecha = entry['published_parsed']
    documento = {"titulo": titulo, "url": url, "fecha": from_datetime_struct_to_timestamp(fecha)}
    document = torrents.find_one(documento)
    if document:
        print "'", unicode_functions.printable_string(titulo), "' already processed, skipping"
    else:
        is_included = included(titulo)
        is_excluded = excluded(titulo)
        documento['incluido'] = is_included
        documento['excluido'] = is_excluded
        if is_excluded:
            print "filter discards '", unicode_functions.printable_string(titulo), "'"
        else:
            if is_included:
                print "downloading ", unicode_functions.printable_string(titulo), " at url ", url
                html = download_file.download_url_html(url)
                esperar = True
                magnets = download_file.download_magnet_in_html_regex(html)
                for magnet in magnets:
                    DownloadStation.add_task(magnet, security_id)
                documento['descargado'] = True
            else:
                print "filter does not include '", unicode_functions.printable_string(titulo), "'"
                notify_mobile_phone(titulo + " not included", url)  # lets you download it manually
                documento['notificado'] = True
        torrents.insert(documento)
    if esperar:
        print "waiting 10 seg..."
        time.sleep(10)  # wait 10 seconds trying not to trigger server DOS counter measures


def get_mongo_client():
    connection = pymongo.MongoClient(config['mongodb']['host'], config['mongodb']['port'])
    return connection


def reload_includes():
    """ Returns all in unicode fron MongoDB """
    result = []
    connection = get_mongo_client()
    the_includes = connection.descargas.includes.find()
    for include in the_includes:
        result.append({'cadena': include['cadena'], 'destino': include['destino']})
    connection.close()
    return result

includes = reload_includes()


def reload_excludes():
    """ Returns all in unicode fron MongoDB """
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
    print "searching includes that were previously skipped"
    connection = get_mongo_client()
    security_id = General.login(session_name())
    torrents = connection.descargas.torrents
    """
    we go through includes checking if something that was not included neither
    excluded can be now marked as included
    """
    for include in includes:
        # print "checking include ", include['cadena'], " to see if we left something..."
        documento = {"titulo": re.compile(include['cadena'], re.IGNORECASE), "incluido": False, "excluido": False}
        for doc in torrents.find(documento):
            # we check if it has been downloaded by exact title
            titulo = doc['titulo']
            url = doc['url']
            if excluded(titulo):
                print "se encontro ", titulo, " que esta incluido por ", include['cadena'], \
                    " pero no se descarga por estar tambien excluido"
            else:
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
                    print "updated document to remember that it was already downloaded, waiting 10 seg..."
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
            title = unicode_functions.welcome_string(task['title'])
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
                notify_mobile_phone(errorMoving, str(sys.exc_info()))
                traceback.print_exc()
            try:
                say.say("estoy quitando la marca elite torrent a todos los ficheros de pelis y series")
                quitar_elitetorrent.quitar_elitetorrent()
            except:
                print "Unexpected error removing elitetorrent from files' names:", sys.exc_info()
                notify_mobile_phone("Unexpected error emoving elitetorrent from files' names", str(sys.exc_info()))
                traceback.print_exc()
            try:
                say.say("estoy repasando por si me he dejado algo por bajar")
                download_previously_not_included()
            except:
                print "Unexpected error downloading previously not included tasks:", sys.exc_info()
                notify_mobile_phone("Unexpected error downloading previously not included", str(sys.exc_info()))
                traceback.print_exc()
            try:
                say.say("contactando con elitetorrent, viendo si hay algo nuevo")
                read_elitetorrent()
            except:
                print "Unexpected error reading elitetorrent:", sys.exc_info()
                notify_mobile_phone("Unexpected error reading elitetorrent", str(sys.exc_info()))
                traceback.print_exc()
            say.say("hasta dentro de 2 horas!")
            print("waiting 2 hours to ask again...")
            time.sleep(60 * 60 * 2)  # 1 hour
            config = reload_config()
            includes = reload_includes()
            excludes = reload_excludes()
    except KeyboardInterrupt:
        print "finishing..."
        sys.exit()
