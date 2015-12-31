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
from subprocess import call

#     The ping utility exits with one of the following values:
#     0                  At least one response was heard from the specified host.
#     2                  The transmission was successful but no responses were received.
#     any other value    An error occurred.  These values are defined in <sysexits.h>.


def is_iphone_present(iphone_ip):
    result = call(["ping","-c 1", "-W 150", "-q", iphone_ip])
    return result == 0
