from Utils import Utils
import threading,Queue,time,sys,traceback
from time import sleep
from sets import Set
import optparse


from ResponseGenerator  import *
from RequestGenerator   import *
from ResourceDetails    import *
from LinkSetGenerator   import Crawler

maximumSites = int(Utils.getConfig("maximumSites"))
threadLimiter = threading.BoundedSemaphore(maximumSites)

#Globals (start with a captial letter)
Qin  = Queue.Queue() 
Qout = Queue.Queue()
Qerr = Queue.Queue()
Pool = []   

def err_msg():
    trace= sys.exc_info()[2]
    try:
        exc_value=str(sys.exc_value)
    except:
        exc_value=''
    return str(traceback.format_tb(trace)),str(sys.exc_type),exc_value

def get_errors():
    try:
        while 1:
            yield Qerr.get_nowait()
    except Queue.Empty:
        pass

def process_queue():
    flag='ok'
    while flag !='stop':
        threadLimiter.acquire()
        try:
            flag,httpObj=Qin.get() #will wait here!
            if flag=='ok':
                httpObj.handleRequest()
                Qout.put(httpObj)
        except:
            Qerr.put(err_msg())
        finally:
            threadLimiter.release()
            
def start_threads(amount=100):
    for i in range(amount):
        thread = threading.Thread(target=process_queue)
        thread.start()
        Pool.append(thread)

def put(data,flag='ok'):
    Qin.put([flag,data]) 

def get(): return Qout.get() #will wait here!

def get_all():
    try:
        while 1:
            yield Qout.get_nowait()
    except Queue.Empty:
        pass

def stop_threads():
    for i in range(len(Pool)):
        Qin.put(('stop',None))
    while Pool:
        time.sleep(10)
        for index,the_thread in enumerate(Pool):
            if the_thread.isAlive():
                continue
            else:
                del Pool[index]
            break


__nanme__ = "CacheMeter"
__version__ = "1.0"
__author__ = "Sagar Sugandhi"
__author_email__ = "sagar dot sugandhi at gmail dot com"
USAGE = "%prog [options]"
VERSION = "%prog v" + __version__
DEBUG = 0

def parse_options():
    """parse_options() -> opts, args

    Parse any command-line options given returning both
    the parsed options and arguments.
    """

    parser = optparse.OptionParser(usage=USAGE, version=VERSION)

    parser.add_option("-f", "--file",
            action="store", default=Utils.getConfig("defaultFile"), dest="file",
            help="Read the site name from external file")

    parser.add_option("-s", "--site-name",
            action="store", default="", dest="sitename",
            help="Get links for specified url only")

    opts, args = parser.parse_args()

    return opts, args

error = False
listSites = Set()

opts, args = parse_options()

if opts.sitename != "":
    print "sitename found"
    listSites.add(opts.sitename)
else:
    try:
        listSites = Utils.readFile(opts.file)
    except:
        print "Error while processing the site input file. Please check the file." + " File name: " + opts.file
        error = True

if str(args[0]) == "1":
    for site in listSites: 
        try:
            with open("../data/linkset/" + site.strip() + ".linkset"):
                print "exists"
                continue
        except:
            crawler = Crawler("http://www." + site.strip(), site.strip(), 30)
            crawler.crawl()
            f1=open("../data/linkset/" + site.strip() + ".linkset", 'w')
            for link in crawler.linkset:
                f1.write(link + "\n")
            f1.close()

elif str(args[0]) == "2":
    requestGenerator = RequestGenerator()
    requestGenerator.start(listSites)

else:
    countSites = 0
    if error!=True:
        for site in listSites: 
            httpObj = HTTPReqRes(site)
            try:
                with open("../data/responses/" + site.rstrip() + '.response'):
                    continue
            except IOError:
                httpObj.normalizeRequestList()
                put(httpObj)
                countSites += 1

        start_threads(countSites)
        stop_threads()

        for i in get_all(): 
            print 'done'

        for i in get_errors(): print i

        for site in listSites:
            sd = SiteDetails(site)
            sd.deserialize()
            sd.cacheStatusIdentifier()
            sd.addCountPerResourceToFile()  