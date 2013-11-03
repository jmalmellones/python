__author__ = 'jmalmellones'
import feedparser


d = feedparser.parse('http://www.elitetorrent.net/rss.php')
print(d)

