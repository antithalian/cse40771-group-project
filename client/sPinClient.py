#!/usr/bin/env python3
# John Sullivan (jsulli28), Jozef Porubcin (jporubci)
# sPin


# http.client: to get catalog
# json: to parse catalog
# random: to randomize the order of entries in the catalog
# time: to check if a peer has timed out
# socket: to connect to a peer
# uuid: to uniquely identify copies of a file across time
# os: to get size of file for sending file as a message using TCP

import http.client
import json
import random
import time
import socket
import uuid
import os


# CATALOG_SERVER: address and port of name server
# ENTRY_TYPE: personal identifier for distinguishing which entries in the catalog are sPin servers
# TIMEOUT: maximum seconds since any given sPin peer last communicated with the name server before the sPin peer is considered dead

CATALOG_SERVER = 'catalog.cse.nd.edu:9097'
ENTRY_TYPE = 'sPin'
TIMEOUT = 60


class sPinPeer:
    def __init__(self, address, port, lastheardfrom):
        self.address = address
        self.port = port
        self.lastheardfrom = lastheardfrom

class sPinClient:
    def __init__(self):
        # TCP socket
        self.s = None
        
        
    # Connects self's socket to a live sPin peer
    def _lookup_peer(self):
        
        # Get catalog
        http_conn = http.client.HTTPConnection(CATALOG_SERVER)
        http_conn.request('GET', '/query.json')
        
        # Parse catalog
        catalog = json.loads(http_conn.getresponse().read())
        
        # Shuffle catalog
        random.shuffle(catalog)
        
        # Iterate through catalog
        for entry in catalog:
            
            # If the entry dict has the necessary keys
            if all(key in entry for key in ('type', 'address', 'port', 'lastheardfrom')):
                
                # If the entry is a live sPin peer
                if entry['type'] == ENTRY_TYPE and entry['lastheardfrom'] >= time.time_ns() / 1000000000.0 - TIMEOUT:
                    
                    # Try to connect to the peer
                    try:
                        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.s.connect((entry['address'], entry['port']))
                    except:
                        self.s.close()
        
        print('Failed to connect to a live peer')
        
        
    # Adds a file to the network
    def sPinADD(self, filepath):
        
        self._lookup_peer()
        if self.s == None:
            pass
        
        # HTTP POST to peer
        try:
            f = open(filepath, 'r')
        except:
            print('Failed to open file: ' + filepath)
            return
        
        # Send message
        # TODO: If the file is too large, could there be a memory error?
        
        #print((60 + os.path.getsize(filepath)).to_bytes(8, 'little') + json.dumps({'uuid': str(uuid.uuid4()), 'data': f.read()}).encode())
        self.s.sendall((60 + os.path.getsize(filepath)).to_bytes(8, 'little') + json.dumps({'uuid': str(uuid.uuid4()), 'data': f.read()}).encode())
        
        f.close()
        '''
        message_buffer = dict()
        message_buffer['uuid'] = str(uuid.uuid4())
        message_buffer['data'] = f.read()
        f.close()
        
        message = json.dumps(message_buffer).encode()
        message_size = len(message).to_bytes(8, 'little')
        
        # Send message
        self.s.sendall(message_size + message)
        '''
        
        
    # Gets the file associated with the given key
    def sPinGET(self, key):
        
        self._lookup_peer()
        if self.s == None:
            return
        
        # HTTP GET to peer
        pass
        
        
    # Requests deletion of the file associated with the given key
    def sPinDEL(self, key):
        
        self._lookup_peer()
        if self.s == None:
            return
        
        # HTTP POST to peer
        pass
