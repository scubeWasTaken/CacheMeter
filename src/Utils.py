from ConfigParser import SafeConfigParser
import os

configFile = "../config/config.ini"

class Utils:
    
    @staticmethod
    #This method returns the configuration setting read from the config file    
    def getConfig(key, option="general"):
        parser = SafeConfigParser()
        parser.read(configFile)
        return parser.get(option, key)
    
    @staticmethod
    def readFile(fileName):
        f = open(fileName)
        lines = f.readlines()
        f.close()
        return lines

    @staticmethod
    def moveHttpRequestFile(targetName):
        execScript("bash_script_move.sh", targetName)

    @staticmethod
    def execScript(scriptName, parameter=""):
        print "sh ../scripts/" + scriptName + " " + parameter
        os.system("sh ../scripts/" + scriptName + " " + parameter   )
