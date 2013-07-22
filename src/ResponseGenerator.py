from Utils import Utils
from sets import Set
import time
import threading
import urllib2
import httplib
import urlparse
from collections import defaultdict
from datetime import datetime
import socket
import global_vars

from ResourceDetails import SiteDetails
from ResourceDetails import ResourceDetails


class HeadRequest(urllib2.Request):
    def get_method(self):
        return "GET"

class HTTPReqRes:

    def __init__(self, URL):
        self.URL = URL
        self.requestFileRaw = Utils.getConfig("requestFolder") + URL.rstrip() + ".request_raw"
        self.requestFile = Utils.getConfig("requestFolder") + URL.rstrip() + ".request"
        self.responseFile = Utils.getConfig("responseFolder") + URL.rstrip() + ".response"
        self.completeResponseStringForAllLinks = ""

    #Removes referrer, GET keyword and also removes redundant requests and creates a new file 
    def normalizeRequestList(self):
        #print "\nIn Normalize request\n"
        uniqueURLs = Set()
        try:
            with open(self.requestFileRaw) as f:
                for line in f:
                    breakflg=0;
                    arr = line.split(" ")
                    for val in arr:
                        if breakflg == 1:
                            uniqueURLs.add(val)

    #RFC 2616 states that Some HTTP methods MUST cause a cache to invalidate an entity. This is either the entity referred to by the Request-URI, or by the Location or Content-Location headers (if present). These methods are:

    #  - PUT
    #  - DELETE
    #  - POST

    #Hence only considered GET
                        if val == "GET":
                            breakflg=1;
            request_fd = open(self.requestFile,"w+")
            request_fd.write("".join(uniqueURLs))
            request_fd.close()
        except:
            print "Error in normalize request"

    #Form request, get response and process Response
    def handleRequest(self):
        #1. Form request object
        #2. Get response
        #3. Process and print response header
        #print "\nIn handle request"
        print "PROCESSING " + self.URL.rstrip() + " START"

        sitedetail = SiteDetails(self.URL.rstrip())

        cacheableObjects = 0
        totalObjects = 0

        mynumbers = []
        print self.requestFile
        with open(self.requestFile) as f:
            
            for val in f:
                rd = ResourceDetails(self.URL.rstrip())
                rd.url = val.strip()
        
                #CHECK IS THE URL IS HTTPS...
                if val.find('https') == 0:
                    rd.isHTTPS = 1

                #request = urllib2.Request(val, unverifiable=True)
                request = HeadRequest(val)
                try:
                    response = urllib2.urlopen(request, timeout=2)
                except urllib2.URLError, e:
                    if isinstance(e.reason, socket.timeout):
                        print("%s -> There was an timeout error: %r %s" % (self.URL.rstrip(), e, val))
                    #else:
                        #print "Error in URL: " + val #+ " Reason: " + str(e.reason)
                    continue
                except urllib2.HTTPError, e:
                    #print "Error in processing HTTP for URL: " + val #+ " Reason: " + str(e.reason)
                    continue
                except:
                    #print "Unknown error in URL: " + val
                    continue

                rd.receivedDate = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

                code = response.getcode()
                
                if code in [500,501,502,503,504,505]:
                    continue
                if code in [400,401,402,403,404,405,406,407,408,409,411,412,413,414,415,416,417]:
                    continue
                if code in [303,304,305]:
                    continue

                keys = response.info().items()

                d = defaultdict(list)
                for k,v in keys:
                    d[k].append(v)

                try:
                    size = str(response.read().__sizeof__())
                except:
                    if "".join(d['transfer-encoding']) != "":
                        size='N/A'
                    elif "".join(d['content-length']) == "":
                        size='N/A'
                    else:
                        size="".join(d['content-length'])


                rd.contentLength = size
                rd.statusCode = str(code)
                rd.contentType = ",".join(d['content-type'])
    
                #Age is used to determine if the item in cache is fresh or not. So, it for post processing. It does not determin while storing that the object is cacheable or not.
                #age        = "".join(d['age']).strip()
                
                rd.lastModified     = "".join(d['last-modified']).strip()
                rd.expires  = "".join(d['expires']).strip()
                rd.pragma       = "".join(d['pragma']).strip()
            
            
                #_______________________________________________________________________
                cacheControl = ",".join(d['cache-control'])
                cacheControlArray = cacheControl.split(",")

                for record in cacheControlArray:
                    #CACHE CONTROL DIRECTIVES THOSE ARE CONSIDERED IN THE ALGORITHM
                    if record.find("public")>=0:
                        rd.isPublic = 1
                    if record.find("private")>=0: 
                        rd.isPrivate = 1
                    if record.find("no-store")>=0:
                        rd.isNoStore = 1
                    if record.find("no-cache")>=0:
                        rd.isNoCache = 1

                    if record.find("max-age") >= 0:
                        try:
                            rd.maxAge=record.split("=")[1]
                        except:
                            rd.maxAge=-222

                    if record.find("must-revalidate") >= 0:
                        rd.mustRevalidate = 1

                    ###NOT-CONSIDERED##
                        #no-transform
                        #proxy-revalidate
                        #s-maxage
                        #cache-extension
                    ####################
                #--------------------------------------------------------------------

                vary = "".join(d['vary']).strip()
                if vary.find("*") >= 0:
                    rd.isVaryValidationForced = 1

                sitedetail.addResource(rd)
                totalObjects += 1
                if totalObjects >= 1000:
                    break
                #print rd.url

        sitedetail.serialize()                  
        print "PROCESSING " + self.URL.rstrip() + " DONE"
