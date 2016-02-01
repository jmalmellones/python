# coding=UTF-8
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

class Update(object):
    """
    its a custom update built upon the telegram update

    description from https://core.telegram.org/bots/api (only one of the
    optional parameters can be in an update at the same time):

    Field                    Type               Description
    update_id                Integer            The update's unique identifier.
                                                Update identifiers start from a
                                                certain positive number and
                                                increase sequentially.
    message                 Message             Optional. New incoming message
                                                of any kind — text, photo,
                                                sticker, etc.
    inline_query            InlineQuery         Optional. New incoming inline
                                                query
    chosen_inline_result    ChosenInlineResult  Optional. The result of an
                                                inline query that was chosen by
                                                a user and sent to their chat
                                                partner.
    """
    tipo = "accion"
    source = None
    def __init__(self, telegramUpdate):
        self.source = telegramUpdate

    def getTipo(self):
        return self.tipo

    def getMessage(self):
        if 'message' in self.source:
            return self.source['message']
        return None

    def getQuery(self):
        if 'inline_query' in self.source:
            return self.source['inline_query']
        return None

    def getChosenResult(self):
        if 'chosen_inline_result' in self.source:
            return self.source['chosen_inline_result']
        return None

    def toString(self):
        message = self.source['message']
        salida = "\nUpdate(\nfecha={0}\ntext={1}\nusername={2}\n)" \
        .format(message['date'], message['text'], message['from']['username'])
        return salida

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


if __name__ == "__main__":
    while True:
        updates = getUpdates(60*60)
        for update in updates:
            a = Update(update)
            print a.getQuery()
            print a.getMessage()
            print a.getChosenResult()
        #print "updates: ", updates
