__author__ = 'jmalmellones'
import feedparser
import download_file
import time


d = feedparser.parse('http://www.elitetorrent.net/rss.php')

if d['status'] == 200:
    print('todo ok, vamos a leer el feed')
    for entry in d['entries']:
        titulo = entry['title_detail']['value']
        url = entry['link']
        print "descarga ", titulo, " en url ", url
        try:
            download_file.descargar_magnet_en_url(url)
        except UnicodeDecodeError:
            print "error bajando url ", url
        time.sleep(5)
else:
    print('no hemos recibido un status 200, algo paso con el feed, saliendo...')


