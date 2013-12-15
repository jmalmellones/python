__author__ = 'jmalmellones'

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