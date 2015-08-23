# -*- coding: utf-8 -*-
from ZehrsLoblawsAccessibility import ZehrsLoblaws
from SobeysAccessibility import Sobeys
from Logger import Logger, CSVWriter
import datetime

infoFile = "../LogFiles/uploadZehrsLoblaws.info"
errFile = "../LogFiles/uploadZehrsLoblaws.err"
debugFile = "../LogFiles/uploadZehrsLoblaws.dbg"
logger = Logger(infoFile, errFile, debugFile)
infoFile2 = "../LogFiles/sobeys.info"
errFile2 = "../LogFiles/sobeys.err"
debugFile2 = "../LogFiles/sobeys.dbg"
logger2 = Logger(infoFile2, errFile2, debugFile2)

csvWriter1 = CSVWriter("zehrs")
csvWriter2 = CSVWriter("loblaws")
csvWriter3 = CSVWriter("sobeys")


zehrs = ZehrsLoblaws("zehrs", logger, csvWriter1)
loblaws = ZehrsLoblaws("loblaws", logger, csvWriter2)
sobeys = Sobeys("sobeys", logger2, csvWriter3)

#print("ZEHRS\n")
#zehrs.parse()
#print("\n\n\nLOBLAWS\n")
#loblaws.parse()
sobeys.parse()

logger.close()
logger2.close()
csvWriter1.close()
csvWriter2.close()
csvWriter3.close()
