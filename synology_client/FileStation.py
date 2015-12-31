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

def list_shares(security_id):
    api_path = 'FileStation/file_share.cgi'
    data_dict = {'api': 'SYNO.FileStation.List', 'version': 1, 'method': 'list_share', '_sid': security_id}
    result = General._synology_call(api_path, data_dict)
    if not result['success']:
        print 'error in list_shares: ', General._error_to_string(result['error']['code'])
    return result

def list(folder, security_id):
    api_path = 'FileStation/file_share.cgi'
    data_dict = {'api': 'SYNO.FileStation.List', 'version': 1, 'method': 'list', 'folder_path': folder, '_sid': security_id}
    result = General._synology_call(api_path, data_dict)
    if not result['success']:
        print 'error in list: ', General._error_to_string(result['error']['code'])
    return result

def get_info(item, security_id):
    api_path = 'FileStation/file_share.cgi'
    data_dict = {'api': 'SYNO.FileStation.List', 'version': 1, 'method': 'getinfo', 'path': item, '_sid': security_id}
    result = General._synology_call(api_path, data_dict)
    if not result['success']:
        print 'error in get_info: ', General._error_to_string(result['error']['code'])
    return result

def move(item, dest_path, security_id):
    api_path = 'FileStation/file_MVCP.cgi'
    data_dict = {'api': 'SYNO.FileStation.CopyMove', 'version': 1, 'method': 'start', 'path': item,
                 'dest_folder_path': dest_path, 'overwrite': True, 'remove_src': True, '_sid': security_id}
    result = General._synology_call(api_path, data_dict)
    if result['success']:
        return True
    else:
        print 'error requesting move: ', General._error_to_string(result['error']['code'])
        return False

def create_folder(folder_path, name, security_id):
    api_path = 'FileStation/file_crtfdr.cgi'
    data_dict = {'api': 'SYNO.FileStation.CreateFolder', 'version': 1, 'method': 'create', 'folder_path': folder_path,
                 'name': name, '_sid': security_id}
    print data_dict
    result = General._synology_call(api_path, data_dict)
    if result['success']:
        return True
    else:
        print 'error in create_folder: ', General._error_to_string(result['error']['code'])
        return False

def test():
    try:
        id = General.login('test')
        ds_shares = list_shares(id)
        for share in ds_shares['data']['shares']:
            print share
        ds_files = list('/public/downloaded', id)
        for file in ds_files['data']['files']:
            if not file['isdir']:
                print file

        General.logout('test')
    except:
        print "error..."


if __name__ == "__main__":
    test()
