#!/usr/bin/env python3

# John Sullivan (jsulli28), Jozef Porubcin (jporubci)
# TestClient.py

from sPinClient import sPinClient

sClient = sPinClient()
sClient.server_lookup()

for server in sClient.servers:
    print(str(server.address) + ', ' + str(server.port) + ', ' + str(server.lastheardfrom))
