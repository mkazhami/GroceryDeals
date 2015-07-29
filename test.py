# -*- coding: utf-8 -*-
from ZehrsLoblawsAccessibility import ZehrsLoblaws
import datetime

print(datetime.datetime.now())

zehrs = ZehrsLoblaws("zehrs")
loblaws = ZehrsLoblaws("loblaws")

print("ZEHRS\n")
zehrs.parse()
print("\n\n\nLOBLAWS\n")
loblaws.parse()


print(datetime.datetime.now())