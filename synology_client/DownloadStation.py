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
from synology_client import General


def add_task(task_url, security_id):
    api_path = 'DownloadStation/task.cgi'
    data_dict = {'api': 'SYNO.DownloadStation.Task', 'version': 1, 'method': 'create',
                 'uri': task_url, '_sid': security_id}
    result = General._synology_call(api_path, data_dict)
    if result['success']:
        return True
    else:
        print 'error in add_task: ', General._error_to_string(result['error']['code'])
        return False


def get_config(security_id):
    api_path = 'DownloadStation/info.cgi'
    data_dict = {'api': 'SYNO.DownloadStation.Info', 'version': 1, 'method': 'getconfig', '_sid': security_id}
    result = General._synology_call(api_path, data_dict)
    if not result['success']:
        print 'error in get_config: ', General._error_to_string(result['error']['code'])
    return result


def get_info(security_id):
    api_path = 'DownloadStation/info.cgi'
    data_dict = {'api': 'SYNO.DownloadStation.Info', 'version': 1, 'method': 'getinfo', '_sid': security_id}
    result = General._synology_call(api_path, data_dict)
    if not result['success']:
        print 'error in get_info: ', General._error_to_string(result['error']['code'])
    return result


def get_tasks(security_id):
    api_path = 'DownloadStation/task.cgi'
    data_dict = {'api': 'SYNO.DownloadStation.Task', 'version': 1, 'method': 'list', '_sid': security_id}
    result = General._synology_call(api_path, data_dict)
    if not result['success']:
        print 'error in get_tasks: ', General._error_to_string(result['error']['code'])
    return result


def delete_task(id, security_id):
    api_path = 'DownloadStation/task.cgi'
    data_dict = {'api': 'SYNO.DownloadStation.Task', 'version': 1, 'method': 'delete', 'id': id, '_sid': security_id}
    result = General._synology_call(api_path, data_dict)
    if result['success']:
        return True
    else:
        print 'error in delete_task: ', General._error_to_string(result['error']['code'])
        return False


def test():
    try:
        id = General.login('test')
        ds_info = get_info(id)
        print ds_info
        ds_config = get_config(id)
        print ds_config
        ds_tasks = get_tasks(id)
        for task in ds_tasks['data']['tasks']:
            print task
        delete_task('dbid_943', id)
        ds_tasks = get_tasks(id)
        for task in ds_tasks['data']['tasks']:
            print task
        General.logout('test')
    except:
        print "error..."


if __name__ == "__main__":
    test()
