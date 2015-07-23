# -*- coding: utf-8 -*-
from ZehrsLoblaws import ZehrsLoblaws

zehrs = ZehrsLoblaws("zehrs")
loblaws = ZehrsLoblaws("loblaws")

print("ZEHRS\n")
zehrs.parse()
print("\n\n\nLOBLAWS\n")
loblaws.parse()