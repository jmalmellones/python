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

def getMe():
    target_url = '{0}/{1}'.format(url, 'getMe')
    return requests.get(target_url).json()


def getUpdates():
    target_url = '{0}/{1}'.format(url, 'getUpdates')
    return requests.get(target_url).json()


def sendMessage(texto):
    target_url = '{0}/{1}'.format(url, 'sendMessage')
    parameters = {'chat_id': chat_id, 'text': texto}
    r = requests.post(target_url, data = parameters)
    return r.json()

if __name__ == "__main__":
    print url
    print getMe()
    print getUpdates()
    print sendMessage("hola")
