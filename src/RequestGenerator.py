from Utils import Utils
from selenium import webdriver
import time

class RequestGenerator:
	fp = None
	
	def __init__(self, profile=Utils.getConfig("profile", "firefox")):
		#1. Add HTTP-Request Logger extension to Firefox
		#2. Set Firefox profile so that HTTP-Request Logger will be available
		self.fp = webdriver.FirefoxProfile(profile)

	#start generation of HTTP Request for resources on supplied webpage
	def start(self, URLlist):
		#code to start the browser
		browser = webdriver.Firefox(self.fp)
		browser.set_page_load_timeout(5)
		#Each URL has a precalculated link set associated with it which contains URL's.
		
		for url in URLlist:
			try:
   				with open("../data/requests/" + url.rstrip() + '.request_raw'): 
					#Website already processed.
					continue
			except IOError:
				print 'Error while opening the raw request file. Regenerating request.'

			linkSetFileName = "../data/linkset/" + url.rstrip() + ".linkset"
			
			linkSet = Utils.readFile(linkSetFileName)
			for link in linkSet:
				try:
					if link.find("http")<0:
						browser.get("http://" + link) # Load page
					else:
						browser.get(link)
				except:
					#print "error while processing " + link
					continue

				time.sleep(0.5)

			while True:
				try:
					browser.get("")
					break
				except:
					time.sleep(0.3)
					continue

			time.sleep(0.3)
			Utils.execScript("bash_script_move.sh", url)

			time.sleep(0.5)
		browser.close()
