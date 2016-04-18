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

#uncomment to create config file
#config = {'https': True, 'server': '192.168.1.1', 'port': 5001, 'user': 'admin', 'password': 'xxx'}
#json.dump(config, open('synology_client.json', 'w'))

#load config
config = json.load(open('synology_client.json'))

server = 'http'
if config['https']:
    server += 's'
server += '://' + config['server'] + ':' + str(config['port']) + '/webapi/'

print('using server ' + server)


def login(session_name):
    if _synology_is_online():
        api_path = 'auth.cgi'
        data_dict = {'api': 'SYNO.API.Auth', 'version': 2, 'method': 'login', 'account': config['user'],
                     'passwd': config['password'], 'session': session_name, 'format': 'sid'}
        result = _synology_call(api_path, data_dict)
        if result['success']:
            return result['data']['sid']
        else:
            print('error obtaining security id')
    else:
        print('cant access diskstation')


def logout(session_name):
    api_path = 'auth.cgi'
    data_dict = {'api': 'SYNO.API.Auth', 'version': 2, 'method': 'logout', 'session': session_name}
    result = _synology_call(api_path, data_dict)
    if result['success']:
        print('logout ok')
    else:
        print('problem in logout')


#makes an api call to synology nas and returns response json
def _synology_call(api_path, data_dict):
    data = urllib.urlencode(data_dict)
    if config['debug']:
        print server + api_path + '?' + data
    r = urllib2.urlopen(server + api_path, data)
    r2 = r.read()
    return json.loads(r2)


#returns true if synology is online
def _synology_is_online():
    syno_api_path = 'query.cgi'
    data_dict = {'api': 'SYNO.API.Info', 'version': 1, 'method': 'query', 'query': 'SYNO.API.Auth'}
    result = _synology_call(syno_api_path, data_dict)

    if result['success']:
        print('all ok, diskstation online')
        return True
    else:
        print('error, diskstation is not online')
        return False


def _error_to_string(error):
    try:
        return {100: 'Unknown error',
                101: 'Invalid parameter',
                102: 'The requested API does not exist',
                103: 'The requested method does not exist',
                104: 'The requested version does not support the functionality',
                105: 'The logged in session does not have permission',
                106: 'Session timeout',
                107: 'Session interrupted by duplicate login',
                400: 'Invalid parameter of file operation',
                401: 'Unknown error of file operation',
                402: 'System is too busy',
                403: 'Invalid user does this file operation',
                404: 'Invalid group does this file operation',
                405: 'Invalid user and group does this file operation',
                406: 'Cant get user or group information from the account server',
                407: 'Operation not permitted',
                408: 'No such file or directory',
                409: 'Non-supported file system',
                410: 'Failed to connect internet-based file system (ex: CIFS)',
                411: 'Read-only file system',
                412: 'Filename too long in the non-encrypted file system',
                413: 'Filename too long in the encrypted file system',
                414: 'File already exists',
                415: 'Disk quota exceeded',
                416: 'No space left on device',
                417: 'Input/output error',
                418: 'Illegal name or path',
                419: 'Illegal file name',
                420: 'Illegal file name on FAT file system',
                421: 'Device or resource busy',
                599: 'No such task of the file operation'}[error]
    except KeyError:
        print 'unknown diskstation error'


#use

#the_session_name = 'DownloadStation'
#sid = login(config['user'], config['password'], the_session_name)
#add_task('any task url admitted by diskstation download station', sid)
#logout(the_session_name)
