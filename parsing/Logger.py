import datetime as datetime

class Logger():

    def __init__(self, info, err, debug):
        self.LOG_FILE_INFO = info
        self.LOG_FILE_ERR = err
        self.LOG_FILE_DEBUG = debug
        self.infoFile = open(self.LOG_FILE_INFO, 'w')
        self.errFile = open(self.LOG_FILE_ERR, 'w')
        self.debugFile = open(self.LOG_FILE_DEBUG, 'w')

    def close(self):
        self.infoFile.close()
        self.errFile.close()
        self.debugFile.close()

    def logInfo(self, msg):
        fullMsg = "[" + str(datetime.datetime.now()) + "] INFO: " + msg + "\n"
        self.infoFile.write(fullMsg)
        self.debugFile.write(fullMsg)

    def logError(self, msg):
        fullMsg = "[" + str(datetime.datetime.now()) + "] ERROR: " + msg + "\n"
        self.infoFile.write(fullMsg)
        self.errFile.write(fullMsg)
        self.debugFile.write(fullMsg)

    def logDebug(self, msg):
        self.debugFile.write("[" + str(datetime.datetime.now()) + "] DEBUG: " + msg + "\n")
        
