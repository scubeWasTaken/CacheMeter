from sets import Set
import time
import json
from pprint import pprint
from Utils import Utils
import re
from datetime import datetime

'''
Images:
image/gif
image/jpeg
image/png

Icons:
image/x-icon

Text:
text/plain
text/html;charset=ISO-8859-1
text/html;charset=UTF-8
text/html
text/css
text/javascript

Application:
application/json
application/x-javascript
application/octet-stream
application/x-shockwave-flash
application/javascript

'''

resourceClassDictionary = dict()
resourceClassDictionary['image/gif'] 	= 'image'
resourceClassDictionary['image/jpeg'] 	= 'image'
resourceClassDictionary['image/png'] 	= 'image'

resourceClassDictionary['image/x-icon'] = 'icon'

resourceClassDictionary['text/plain'] 			= 'text'
resourceClassDictionary['text/html'] 			= 'text'

resourceClassDictionary['text/css'] 			= 'css'

resourceClassDictionary['text/javascript'] 			= 'javascript'
resourceClassDictionary['application/javascript']	= 'javascript'

resourceClassDictionary['application/json'] 		= 'json'

resourceClassDictionary['application/octet-stream'] = 'video'

objectsConsideredCacheable = Set(['javascript', 'css', 'image', 'icon', 'application', 'json'])

def classifyResource(contentType):
	resource = contentType.strip().rstrip(';')
	pattern = re.compile(r'\s+')
	pattern.sub('', resource)
	resource = "".join(resource.split())
	resource = resource.lower()
	#print resource

	try:
		keyDic = resourceClassDictionary[resource]
	except KeyError:
		if resource.find('javascript') >= 0:
			keyDic = 'javascript'
		elif resource.find('css') >= 0:
			keyDic = 'css'
		elif resource.find('video') >= 0:
			keyDic = 'video'
		elif resource.find('text') >= 0:
			keyDic = 'text'
		elif resource.find('icon') >= 0:
			keyDic = 'icon'
		elif resource.find('image') >= 0:
			keyDic = 'image'
		elif resource.find('json') >= 0:
			keyDic = 'json'
		elif resource.find('application') >=0:
			keyDic = 'application'
		elif resource == '':
			#print "None"
			keyDic = 'N/A'
		else:
			keyDic = resource

	return keyDic

	

def object_decoder(obj):
    return ResourceDetails(
        siteName				=	obj['siteName'], 
        url 					=	obj['url'], 
        statusCode 				=	obj['statusCode'], 
        isPublic  				=	obj['isPublic'],
        isPrivate 				=	obj['isPrivate'],
        contentLength			=	obj['contentLength'],
        contentType 			=	obj['contentType'],
        isNoStore				=	obj['isNoStore'],
        isNoCache				=	obj['isNoCache'],
        maxAge 					=	obj['maxAge'],
        lastModified 			= 	obj['lastModified'],
        pragma 					=	obj['pragma'],
        mustRevalidate 			=	obj['mustRevalidate'],
        isVaryValidationForced 	=	obj['isVaryValidationForced'],
        isHTTPS 				= 	obj['isHTTPS'],
        receivedDate			= 	obj['receivedDate']
        )

class ResourceDetails:
	def __init__(self, siteName, url="", statusCode="", contentLength=0, contentType = "", isPublic = 0, isPrivate = 0,isNoStore = 0,isNoCache = 0,maxAge = -222,expires = "",lastModified = "",pragma="",mustRevalidate = 0,isVaryValidationForced = 0, isHTTPS=0, receivedDate=""):
		self.siteName = siteName
		self.url = url

		self.statusCode = statusCode
		self.contentLength = contentLength
		self.contentType = contentType

		self.isPublic = isPublic
		self.isPrivate = isPrivate
		self.isNoStore = isNoStore
		self.isNoCache = isNoCache
		self.maxAge = maxAge

		self.expires = expires 
		self.lastModified = lastModified
		self.pragma = pragma

		self.mustRevalidate = mustRevalidate 
		self.isVaryValidationForced = isVaryValidationForced 

		self.isHTTPS = isHTTPS
		self.receivedDate = receivedDate
	
class SiteDetails:
	def __init__(self, siteName):
		self.siteName = siteName
		self.rdList = Set()

		self.recordIndicator = Set()
		self.dic = dict()
		self.dicCacheCount = dict()
		self.dicTotalCount = dict()
		self.localtime = time.localtime()
		self.httpsCount = 0
		self.httpsCached = 0
		self.cacheableObjectCount = 0
		self.cacheableObjectsThatAreCached = 0
		self.responseFileString = ""

		self.imageCount = 0
		self.imageCached = 0
		self.imageHttps = 0
		self.imageHttpsCached = 0

		self.textCount = 0
		self.textCached = 0
		self.textHttps = 0
		self.textHttpsCached = 0

		self.scriptCount = 0
		self.scriptCached = 0
		self.scriptHttps = 0
		self.scriptHttpsCached = 0

		self.videoCount = 0
		self.videoCached = 0
		self.videoHttps = 0
		self.videoHttpsCached = 0

		self.iconCount = 0
		self.iconCached = 0
		self.iconHttps = 0
		self.iconHttpsCached = 0

		self.appCount = 0
		self.appCached = 0
		self.appHttps = 0
		self.appHttpsCached = 0

		self.sizeDetailSet = Set()

		self.requestFileRaw = Utils.getConfig("requestFolder") + siteName.rstrip() + ".request_raw"
		self.requestFile = Utils.getConfig("requestFolder") + siteName.rstrip() + ".request"
		self.responseFile = Utils.getConfig("responseFolder") + siteName.rstrip() + ".response"

	def addResource(self, rd):
		self.rdList.add(rd)

	def serialize(self):
		
		details = ""

		i = 0

		for resource in self.rdList:
			if i!=0: 
				details += "\r\n"
			i+=1
			details += json.dumps(vars(resource),sort_keys=True, indent=4)
		
		retry = 1
		while(retry < 5):
			try:
				retry += 1
				siteFile=open("../data/responses/"+self.siteName.rstrip()+".response", 'w+')
				siteFile.write(details)
				siteFile.close()
				break
			except:
				print "Error while writing site details info.. retrying..." 

	def deserialize(self):
		#print "deserialize"
		json_file=open("../data/responses/"+self.siteName.rstrip()+".response", 'r')
	    
		json_read = json_file.read()
		individualRec = json_read.split("\r\n")

		for rec in individualRec:
		    try:
		        rd = json.loads(rec, object_hook=object_decoder)
		        self.addResource(rd)
		    except:
		        print "error in deserialize"
		    #else:
		    #	print "deserialize complete"

		json_file.close()

	def incrementCount(self, resourceTypeKey, cacheIndicator=1): 
		#cacheIndicator = 1:cacheable:default, 0:non-cacheable

		try:
			val = self.dic[resourceTypeKey]
		except KeyError:
			self.recordIndicator.add(resourceTypeKey)
			val = 0
		val = val + 1
		self.dic[resourceTypeKey] =  val
		
		if cacheIndicator == 1:
			try:
				totalCachedResource = self.dicCacheCount[resourceTypeKey] + 1
			except:
				totalCachedResource = 1
			self.dicCacheCount[resourceTypeKey] = totalCachedResource

		try:
			totalResource = self.dicTotalCount[resourceTypeKey] + 1
		except:
			totalResource = 1
			self.dicCacheCount[resourceTypeKey] = 0
		self.dicTotalCount[resourceTypeKey] = totalResource
		
		if resourceTypeKey in objectsConsideredCacheable:
			self.cacheableObjectCount += 1
			if cacheIndicator == 1:
				self.cacheableObjectsThatAreCached += 1
		
	def cacheStatusIdentifier(self):

		DEBUG = False
		
		for resourceDetails in self.rdList:
			cached = 0

			maybecached=0

			validators = 0

			if resourceDetails.lastModified != "":
				#http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html  Section 14.21
				#DATE must be in RFC 1123 date format:
				DB_TIME_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
				try:
					parsed = datetime.strptime(resourceDetails.lastModified, DB_TIME_FORMAT)
					validators = 1
				except ValueError:
					if DEBUG:
						print "Error on last modified value : " + expires
					validators = 0
				except:
					validators = 0


			if int(resourceDetails.statusCode) in [200, 203, 206, 300, 301, 410]:
				maybecached = 1

			elif int(resourceDetails.statusCode) in [302, 307]:
				#or resourceDetails.s-maxAge != -222#or proxyrevalidate <> "" 
				if resourceDetails.maxAge != -222 or resourceDetails.isPublic==1 or resourceDetails.isPrivate==1 or resourceDetails.mustRevalidate != 0 or resourceDetails.expires != "":
					maybecached = 1

			if resourceDetails.maxAge>0:
				cached=1

			#Checking on Expiry
			elif resourceDetails.expires != "":
				#http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html  Section 14.21
				#DATE must be in RFC 1123 date format:
				DB_TIME_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
				try:
					parsed = datetime.strptime(resourceDetails.expires, DB_TIME_FORMAT)
					date_today = datetime.utcnow()
					date_received = datetime.strptime(resourceDetails.receivedDate, DB_TIME_FORMAT)
					#IF EXPIRY VALUE IS LESS THAN TODAY, THEN NOT CACHEABLE
					if (date_received >= parsed):
						if DEBUG:
							print "expires -- cached = 0"
						cached = 0
					else:
						cached = 1
				except ValueError:
					if DEBUG:
						print "expires -- cached = 0"
					#print "Error on expiry value : " + expires
					cached = 0
				except:
					#print val
					#print "*********************************"
					cached = 0

			
			if resourceDetails.isNoCache != 0:
				if DEBUG:
					print "no cache -- cached = 0"
				cached = 0
			elif resourceDetails.pragma != "":
				if resourceDetails.pragma.find("no")>=0:
					if DEBUG:
						print "pragma -- cached = 0"
					cached = 0

		
			if resourceDetails.isNoStore != 0:
				if DEBUG:
					print "no store -- cached = 0"
				cached = 0
				validators = 0

			if validators==1 and cached == 0:
				cached = 1

			if resourceDetails.isVaryValidationForced:
				#Found * in VARY header. This wont be used from cache the next time.
				if DEBUG:
					print "vary -- cached = 0"
				cached=0

			if maybecached == 0 and cached==1:
				if DEBUG:
					print "may be cached -- cached = 0"
				cached = 0

			if DEBUG:
				print "------------------------------------------------"
			
			resourceTypeKey = classifyResource(resourceDetails.contentType)

			if cached == 1:
				if resourceDetails.isHTTPS == 1:
					self.httpsCount += 1
					self.httpsCached += 1
		
				self.incrementCount(resourceTypeKey)
			else:
				if resourceDetails.isHTTPS == 1:
					self.httpsCount += 1
				self.incrementCount(resourceTypeKey, 0)

			self.finerDetails(resourceDetails.url, resourceDetails.contentType, resourceDetails.contentLength, cached, resourceDetails.isHTTPS)

	def finerDetails(self, uri, resource, contentSize, cacheIndicator=1, httpsIndicator=0):
		resource = resource.strip().rstrip(';')
		pattern = re.compile(r'\s+')
		pattern.sub('', resource)
		resource = "".join(resource.split())
		resource = resource.lower()

		if resource.find('javascript') >= 0:
			resource_type="script"
			self.scriptCount += 1
			self.scriptCached += cacheIndicator
			if httpsIndicator == 1:
				self.scriptHttps += 1
				self.scriptHttpsCached += cacheIndicator

		elif resource.find('css') >= 0:
			resource_type="script"
			self.scriptCount += 1
			self.scriptCached += cacheIndicator
			if httpsIndicator == 1:
				self.scriptHttps += 1
				self.scriptHttpsCached += cacheIndicator

		elif resource.find('video') >= 0:
			resource_type="video"
			self.videoCount += 1
			self.videoCached += cacheIndicator
			if httpsIndicator == 1:
				self.videoHttps += 1
				self.videoHttpsCached += cacheIndicator

		elif resource.find('text') >= 0:
			resource_type="text"
			self.textCount += 1
			self.textCached += cacheIndicator
			if httpsIndicator == 1:
				self.textHttps += 1
				self.textHttpsCached += cacheIndicator

		elif resource.find('icon') >= 0:
			resource_type="icon"
			self.iconCount += 1
			self.iconCached += cacheIndicator
			if httpsIndicator == 1:
				self.iconHttps += 1
				self.iconHttpsCached += cacheIndicator
		
		elif resource.find('image') >= 0:
			resource_type="image"
			self.imageCount += 1
			self.imageCached += cacheIndicator
			if httpsIndicator == 1:
				self.imageHttps += 1
				self.imageHttpsCached += cacheIndicator
		
		elif resource.find('json') >= 0:
			resource_type="script"
			self.scriptCount += 1
			self.scriptCached += cacheIndicator
			if httpsIndicator == 1:
				self.scriptHttps += 1
				self.scriptHttpsCached += cacheIndicator

		elif resource.find('application') >=0:
			resource_type="application"
			self.appCount += 1
			self.appCached += cacheIndicator
			if httpsIndicator == 1:
				self.appHttps += 1
				self.appHttpsCached += cacheIndicator

		else:
			resource_type="other"

		obj = genericResourceDetails(uri, resource_type, contentSize, cacheIndicator, httpsIndicator)
		self.sizeDetailSet.add(obj)

	def addCountPerResourceToFile(self):
		
		resourceStatus = ""

		f1=open("../data/results/0410.txt", 'a+')
		f2=open("../data/results/0410.csv", 'a+')
		f3=open("../data/results/0410-size.csv", 'a+')

		f1.write( "\n" + self.siteName.strip() + " - " + time.strftime("%Y-%m-%d %H:%M:%S", self.localtime) + "\n\n")
		f1.write("%-20s %-10s %-10s %-5s\n\n" % ("Record Type", "Total", "Cached", "Non-Cached"))
		
		totalRecords = 0
		totalCachedRecords = 0
		totalUncachedRecords = 0	
	
		for record in self.recordIndicator:
			f1.write("%-20s %-10s %-10s %-5s\n" % (str(record), str(self.dicTotalCount[record]), str(self.dicCacheCount[record]), str(self.dicTotalCount[record] - self.dicCacheCount[record])))
			
			totalRecords += self.dicTotalCount[record]
			totalCachedRecords += self.dicCacheCount[record]
			totalUncachedRecords += (self.dicTotalCount[record] - self.dicCacheCount[record])

		if totalRecords == 0:
			totalRecords = 1
		if self.httpsCount == 0:
			self.httpsCount = 1
		if self.cacheableObjectCount == 0:
			self.cacheableObjectCount = 1

		if self.imageCount == 0:
			self.imageCount = 1
		if self.imageHttps == 0:
			self.imageHttps = 1
		if self.textCount == 0:
			self.textCount = 1
		if self.textHttps == 0:
			self.textHttps = 1
		if self.scriptCount == 0:
			self.scriptCount = 1
		if self.scriptHttps == 0:
			self.scriptHttps = 1

		f1.write ("%-20s %-10s %-10s %-5s\n" % ("", "-------", "-------", "-------"))
		f1.write ("%-20s %-10s %-10s %-5s\n" % ("", str(totalRecords), str(totalCachedRecords), str(totalUncachedRecords)))
		f1.write ("\nPercent Cached: "  + str((totalCachedRecords * 100)/  totalRecords) + "%\n")
		f1.write ("Objects that fall in cacheable category (Images, Scripts, Application): " + str(self.cacheableObjectCount) + "\n");
		f1.write ("HTTPS Requests: " +  str(self.httpsCount)+ "\n" )
		if self.httpsCount > 0: 
			f1.write ("HTTPS Cached Percent: " + str((self.httpsCached * 100)/ self.httpsCount) + "\n" )
		f1.write ("----------------------------------------\n")
		f1.close()

		#File f2 filling format is as follows:
		#Sr. No. 	Time 	SiteName 	TotalRecords 	TotalCacheableRecords 	TotalUncachedRecords 	TotalCachedPercentage 	TotalHTTPS 	TotalHTTPSCacheable 	HTTPSCacheablePercentage 	CacheableObjects 	CacheableObjectsThatAreCached 	Percentage
		f2.write(time.strftime("%Y%m%d", self.localtime) + "," + 
			self.siteName.strip() + "," + str(totalRecords) + "," + str(totalCachedRecords) 
			+ "," + str(totalUncachedRecords) + "," + str((totalCachedRecords * 100)/  totalRecords) 
			+ "," + str(self.httpsCount) + "," + str(self.httpsCached)
			+ "," + str((self.httpsCached * 100) / self.httpsCount)
			+ "," + str(self.cacheableObjectCount) #totalstr() this was the enclosing function for cacheableObjectCount.. dont know why i added it
			+ "," + str(self.cacheableObjectsThatAreCached)
			+ "," + str((self.cacheableObjectsThatAreCached * 100)/ self.cacheableObjectCount)
			+ "," + str((self.imageCached * 100)/ self.imageCount)
			+ "," + str((self.imageHttpsCached * 100)/ self.imageHttps)
			+ "," + str((self.textCached * 100)/ self.textCount)
			+ "," + str((self.textHttpsCached * 100)/ self.textHttps)
			+ "," + str((self.scriptCached * 100)/ self.scriptCount)
			+ "," + str((self.scriptHttpsCached * 100)/ self.scriptHttps) 
			+ "," + str(self.imageCached)
			+ "," + str(self.imageCount)
			+ "," + str(self.textCached)
			+ "," + str(self.textCount)
			+ "," + str(self.scriptCached)
			+ "," + str(self.scriptCount)
 			+ "\n"
			)

		
		f2.close()

		for sizeDetailItem in self.sizeDetailSet:
			f3.write(self.siteName.strip().rstrip()
				+ "," + sizeDetailItem.resourceType 
				+ "," + str(sizeDetailItem.contentSize)
				+ "," + str(sizeDetailItem.isCached)
				+ "," + str(sizeDetailItem.isHttps)
				+ "," + sizeDetailItem.uri.strip().rstrip() 
				+ "\n")
		f3.close()

class genericResourceDetails:
	def __init__(self, uri, resource, size, isCached, isHttps):
		self.uri = uri
		self.resourceType = resource
		self.contentSize = size
		self.isCached = isCached
		self.isHttps = isHttps