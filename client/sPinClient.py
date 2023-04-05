#!/usr/bin/env python3

# John Sullivan (jsulli28), Jozef Porubcin (jporubci)
# sPinClient.py

import json
import http.client

CATALOG_SERVER = 'catalog.cse.nd.edu:9097'
SERVER_TYPE = 'sPin'

class Server:
    def __init__(self, address, port, lastheardfrom):
        self.address = address
        self.port = port
        self.lastheardfrom = lastheardfrom

class sPinClient:
    def __init__(self):
        self.servers = []
        
        
    def server_lookup(self):
        http_conn = http.client.HTTPConnection(CATALOG_SERVER)
        http_conn.request('GET', '/query.json')
        catalog = json.loads(http_conn.getresponse().read())
        
        self.servers = [Server(server['address'], server['port'], server['lastheardfrom']) for server in catalog if 'type' in server and server['type'] == SERVER_TYPE and 'address' in server and 'port' in server and 'lastheardfrom' in server]
        
        self.servers.sort(reverse=True, key=lambda x: x.lastheardfrom)
        
        
    def sPinGET(self, key):
        pass
