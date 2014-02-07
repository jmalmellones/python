__author__ = 'jmalmellones'
import feedparser
import download_file
import time
import synology_client
import json
import say
import pymongo
import sys
from time import mktime
from datetime import datetime
import prowl_notifier

config_file = 'rss_downloader.json'
config = json.load(open(config_file))


def reload_config():
    return json.load(open(config_file))


def includes():
    return config['includes']


def excludes():
    return config['excludes']


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
    for include in includes():
        if include.lower() in title.lower():
            return True
    return False


def excluded(title):
    """ returns True if title is excluded in the configuration """
    for exclude in excludes():
        if exclude.lower() in title.lower():
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
                    synology_client.add_task(magnet, security_id)
                documento['descargado'] = True
            else:
                print "filter does not include '", titulo, "'"
                notify_using_prowl(titulo + " not included", url)  # lets you download it manually
                documento['notificado'] = True
        torrents.insert(documento)
    if esperar:
        print "waiting 10 seg..."
        time.sleep(10)  # wait 10 seconds trying not to trigger server DOS counter measures


def read_elitetorrent():
    print "reading data from elitetorrent"
    d = feedparser.parse('http://www.elitetorrent.net/rss.php')
    if d['status'] == 200:
        print('status ok, interpreting data')
        connection = pymongo.MongoClient()
        torrents = connection.descargas.torrents
        # respuestas_rss = connection.descargas.respuestas_rss
        security_id = synology_client.login(session_name())
        for theEntry in d['entries']:
            treat_entry(theEntry, security_id, torrents)
        connection.close()
        synology_client.logout(session_name())
    else:
        print("status received from server is not 200, giving up...")

def download_previously_not_included():
    print "searching included that previously were skipped"
    connection = pymongo.MongoClient()
    security_id = synology_client.login(session_name())
    torrents = connection.descargas.torrents
    for include in includes():
        print "checking include ", include, " to see if we left something..."
        documento = {"titulo": {"$regex": include}, "incluido": False, "excluido": False}
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
                    synology_client.add_task(magnet, security_id)
                encontrado['descargado'] = True
                encontrado['incluido'] = True
                torrents.save(encontrado)
                print "updated document to remember that it was already downloaded"
                print "waiting 10 seg..."
                time.sleep(10)  # wait 10 seconds trying not to trigger server DOS counter measures
    synology_client.logout(session_name())
    connection.close()

if __name__ == "__main__":
    try:
        while True:
            # raise Exception('spam', 'eggs')
            download_previously_not_included()
            read_elitetorrent()
            print("waiting 2 hours to ask again...")
            time.sleep(60 * 60 * 2)  # 1 hour
            config = reload_config()
    except KeyboardInterrupt:
        print "finishing..."
        sys.exit()
    except:
        print "Unexpected error:", sys.exc_info()[0]
        notify_using_prowl("Unexpected error", str(sys.exc_info()[0]))  # lets you download it manually
        sys.exit()