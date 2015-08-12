# -*- coding: utf-8 -*-
from ZehrsLoblawsAccessibility import ZehrsLoblaws
from SobeysAccessibility import Sobeys
from Logger import Logger
import datetime

infoFile = "../LogFiles/uploadZehrsLoblaws.info"
errFile = "../LogFiles/uploadZehrsLoblaws.err"
debugFile = "../LogFiles/uploadZehrsLoblaws.dbg"
logger = Logger(infoFile, errFile, debugFile)
infoFile2 = "../LogFiles/sobeys.info"
errFile2 = "../LogFiles/sobeys.err"
debugFile2 = "../LogFiles/sobeys.dbg"
logger2 = Logger(infoFile2, errFile2, debugFile2)


zehrs = ZehrsLoblaws("zehrs", logger)
loblaws = ZehrsLoblaws("loblaws", logger)
sobeys = Sobeys("sobeys", logger2)

#print("ZEHRS\n")
#zehrs.parse()
#print("\n\n\nLOBLAWS\n")
#loblaws.parse()
sobeys.parse()

logger.close()
