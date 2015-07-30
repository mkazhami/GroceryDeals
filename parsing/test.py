# -*- coding: utf-8 -*-
from ZehrsLoblawsAccessibility import ZehrsLoblaws
from Logger import Logger
import datetime

infoFile = "LogFiles/uploadZehrsLoblaws.info"
errFile = "LogFiles/uploadZehrsLoblaws.err"
debugFile = "LogFiles/uploadZehrsLoblaws.dbg"
logger = Logger(infoFile, errFile, debugFile)


zehrs = ZehrsLoblaws("zehrs", logger)
loblaws = ZehrsLoblaws("loblaws", logger)

print("ZEHRS\n")
zehrs.parse()
print("\n\n\nLOBLAWS\n")
loblaws.parse()

logger.close()
