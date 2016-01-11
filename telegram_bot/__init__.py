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
import requests
import json
import urllib2

config = json.load(open('telegram_bot.json'))
api_key = config['api_key']
chat_id = config['chat_id']
url = 'https://api.telegram.org/bot{0}'.format(api_key)
offset = -1

def getMe():
    target_url = '{0}/{1}'.format(url, 'getMe')
    return requests.get(target_url).json()


def getUpdates(seconds):
    global offset
    target_url = '{0}/{1}'.format(url, 'getUpdates')
    parameters = {'timeout': seconds}
    print offset
    if offset is not -1:
        offset += 1
        parameters['offset'] = offset
    print parameters
    result_json = requests.get(target_url, data = parameters).json()
    updates = result_json['result']
    print updates
    num_updates = len(updates)
    if num_updates > 0:
        offset = updates[num_updates - 1]['update_id']
        print "nuevo offset es ", offset
    return updates


def sendMessage(texto):
    target_url = '{0}/{1}'.format(url, 'sendMessage')
    parameters = {'chat_id': chat_id, 'text': texto}
    r = requests.post(target_url, data = parameters)
    return r.json()


def tratarUpdate(update):
    accion = obtenerAccionUpdate(update)
    print "update con accion ", accion, ": ", toString(update)


def obtenerAccionUpdate(update):
    return "abrir"


def toString(update):
    message = update['message']
    salida = "\nUpdate(\nfecha={0}\ntext={1}\nusername={2}\n)".format(message['date'], message['text'], message['from']['username'])
    return salida


if __name__ == "__main__":
    while True:
        updates = getUpdates(60*60)
        for update in updates:
            tratarUpdate(update)
        #print "updates: ", updates
