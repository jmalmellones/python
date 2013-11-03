__author__ = 'jmalmellones'
import feedparser

# returns current temperature in C in location
#location for Mostoles, Madrid (Spain) = 767893


def current_temperature(location):
    d = feedparser.parse('http://weather.yahooapis.com/forecastrss?w=' + str(location) + '&u=c')
    temperature = d['entries'][0]['yweather_condition']['temp']
    return temperature