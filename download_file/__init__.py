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
import urllib2
import re
from HTMLParser import HTMLParser


magnet_regex = 'magnet:[^"]*'


class MyHTMLParser(HTMLParser):
    """
    create a subclass of HTMLParser and override the handler methods to retrieve 'magnet' urls
    """
    en_a = False
    result = []
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
        if self.en_a and self.url.startswith('magnet'):
            self.result.append(self.url)


def download_url_html(url):
    """
    downloads the page in the url (not images or anything, only html)
    """
    e = urllib2.urlopen(url)
    html = e.read()
    return html


def download_magnet_in_html_parser(html):
    """
    downloads all magnet found in the html given with the parser
    """
    parser = MyHTMLParser()
    parser.feed(html)
    return parser.result


def download_magnet_in_html_regex(html):
    """
    downloads all magnet found in the html given with regex
    """
    return re.findall(magnet_regex, html)


#the_url = 'http://www.elitetorrent.net/torrent/21616/carrera-infernal-hdrip'
#the_html = download_url_html(the_url)
#print download_magnet_in_html_regex(the_html)
