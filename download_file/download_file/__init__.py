__author__ = 'jmalmellones'
import urllib2
import urllib

from HTMLParser import HTMLParser


# create a subclass of HTMLParser and override the handler methods to retrieve 'magnet' urls
class MyHTMLParser(HTMLParser):
    en_a = False
    url = ''

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.en_a = True
            for attr, value in attrs:
                if attr == 'href':
                    self.url = value
                    break

    def handle_endtag(self, tag):
        if tag == "a":
            self.en_a = False

    def handle_data(self, data):
        # and data.startswith('Descargar')
        if self.en_a and self.url.startswith('magnet'):
            print self.url


parser = MyHTMLParser()


#descarga todos los magnet encontrados en una url dada
def descargar_magnet_en_url(url):
    e = urllib2.urlopen(url)
    html = e.read()
    parser.feed(html)
