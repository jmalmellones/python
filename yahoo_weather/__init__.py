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
__author__ = 'jmalmellones'
import feedparser

# returns current temperature in C in location
#location for Mostoles, Madrid (Spain) = 767893


def current_temperature(location):
    d = feedparser.parse('http://weather.yahooapis.com/forecastrss?w=' + str(location) + '&u=c')
    temperature = d['entries'][0]['yweather_condition']['temp']
    return temperature
