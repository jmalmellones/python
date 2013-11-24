__author__ = 'jmalmellones'

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
        print(result)
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


def add_task(task_url, security_id):
    api_path = 'DownloadStation/task.cgi'
    data_dict = {'api': 'SYNO.DownloadStation.Task', 'version': 1, 'method': 'create',
                 'uri': task_url, '_sid': security_id}
    result = _synology_call(api_path, data_dict)
    if result['success']:
        print('task creation ok')
    else:
        print('problem creating task ' + task_url)


#makes an api call to synology nas and returns response json
def _synology_call(api_path, data_dict):
    data = urllib.urlencode(data_dict)
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

#use

#the_session_name = 'DownloadStation'
#sid = login(config['user'], config['password'], the_session_name)
#add_task('any task url admitted by diskstation download station', sid)
#logout(the_session_name)
