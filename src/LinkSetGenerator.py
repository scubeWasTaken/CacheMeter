## Referenced from http://code.activestate.com/recipes/576551/

import re
import sys
#import time
#import math
import urllib2
import urlparse
import optparse
from cgi import escape
from traceback import format_exc
from Queue import Queue, Empty as QueueEmpty

import urllib2
from pprint import pprint
from collections import defaultdict
import httplib
import urlparse
import sys

from urllib2 import Request
from BeautifulSoup import BeautifulSoup

__nanme__ = "Mozilla"
__version__ = "21.0.1"

USAGE = "%prog [options] <url>"
VERSION = "%prog v" + __version__
AGENT = "%s/%s" % (__name__, __version__)
DEBUG = True   

class Crawler(object):

    def __init__(self, root, domainCheck, depth, locked=True):
        self.root = root
        self.depth = depth
        self.locked = locked
        self.host = urlparse.urlparse(root)[1]
        self.urls = []
        self.links = 0
        self.followed = 0
        self.linkset = []
        self.domainCheck = domainCheck

    def crawl(self):
        self.linkset.append(self.root)
        page = Fetcher(self.root)
        page.fetch()
        q = Queue()
        for url in page.urls:
            q.put(url)
        followed = [self.root]

        n = 0

        while n<=40:
            try:
                url = q.get(block=True, timeout=3)
            except QueueEmpty:
                break

            n += 1

            if url not in followed:
                try:
                    host = urlparse.urlparse(url)[1]

                    if host.find(self.domainCheck) >= 0:
                        print url
                        self.linkset.append(url)

                        if self.locked and re.match(".*%s" % self.host, host):
                            followed.append(url)
                            self.followed += 1
                            page = Fetcher(url)
                            page.fetch()
                            for i, url in enumerate(page):
                                if url not in self.urls:
                                    self.links += 1
                                    q.put(url)
                                    self.urls.append(url)
                            if n > self.depth and self.depth > 0:
                                break

                    req = Request(url)

                except Exception, e:
                    if DEBUG:
                        print "ERROR in crawl"
                        print e
                        print "-----------"
                        return []

        
class Fetcher(object):

    def __init__(self, url):
        self.url = url
        self.urls = []

    def __getitem__(self, x):
        return self.urls[x]

    def _addHeaders(self, request):
        request.add_header("User-Agent", AGENT)

    def open(self):
        url = self.url
        try:
            request = urllib2.Request(url)
            handle = urllib2.build_opener()
        except IOError:
            return None
        return (request, handle)

    def fetch(self):
        request, handle = self.open()
        self._addHeaders(request)
        if handle:
            try:
                content = unicode(handle.open(request).read(), "utf-8",
                        errors="replace")
                soup = BeautifulSoup(content)
                tags = soup('a')
            except urllib2.HTTPError, error:
                tags = []
            except urllib2.URLError, error:
                tags = []
            for tag in tags:
                href = tag.get("href")
                if href is not None:
                    url = urlparse.urljoin(self.url, escape(href))
                    if url not in self:
                        self.urls.append(url)