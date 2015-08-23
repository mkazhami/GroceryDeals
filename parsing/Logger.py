import datetime as datetime
import csv

projectRootDir = ".."

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
        
    def flush(self):
        self.infoFile.flush()
        self.errFile.flush()
        self.debugFile.flush()

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


class CSVWriter():

    def __init__(self, store_name):
        self.file_name = projectRootDir + "/CsvFiles/" + store_name + "-" + str(datetime.date.today()) + ".csv"
        self.csv_file = open(self.file_name, 'w')
        self.csv_write = csv.writer(self.csv_file, delimiter=',')

    def close(self):
        self.csv_file.close()

    def addItems(self, items):
        self.csv_write.writerows(items)
        
