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
import urllib
import urllib2
import json
import xml.etree.ElementTree as ET

config = json.load(open('prowl_notifier.json'))
api_key = config['api_key']
url = "https://prowl.weks.net/publicapi/add"


def encode_utf_8(texto):
    return unicode(texto).encode('utf-8')


def send_notification(app, event, description):
    f = {'apikey': api_key, 'application': encode_utf_8(app), 'event': encode_utf_8(event),
         'description': encode_utf_8(description)}
    e = urllib2.urlopen(url, urllib.urlencode(f))
    xml = e.read()
    root = ET.fromstring(xml)
    for success in root.findall('success'):
        if '200' == success.get('code'):
            print "notification send ok (", success.get('remaining'), " remaining until ", success.get('resetdate'), ")"
    for error in root.findall('error'):
        print "error ", error.get('code'), " sending notification:", error.text


if __name__ == "__main__":
    """
    we send a test notification
    """
    send_notification('test app', 'test event', 'test description')
