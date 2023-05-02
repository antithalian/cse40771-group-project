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
import requests # for multipart mainly, but using for all now
import json
import random
import time
import socket
import uuid
import math
import os
import hashlib
import sys


# CATALOG_SERVER: address and port of name server
# ENTRY_TYPE: personal identifier for distinguishing which entries in the catalog are sPin servers
# TIMEOUT: maximum seconds since any given sPin peer last communicated with the name server before the sPin peer is considered dead

CATALOG_SERVER = 'catalog.cse.nd.edu:9097'
ENTRY_TYPE = 'sPin'
TIMEOUT = 60
K_DENOM = 3 # denominator for determining k


class sPinPeer:
    def __init__(self, address, port, lastheardfrom):
        self.address = address
        self.port = port
        self.lastheardfrom = lastheardfrom

class sPinClient:
    def __init__(self, main):
        self.main = main
        # TCP socket
        self.s = None
        self.addr = None
        self.port = None
        
    def get_peers(self):
        # Get catalog
        http_conn = http.client.HTTPConnection(CATALOG_SERVER)
        http_conn.request('GET', '/query.json')
        
        # Parse catalog
        catalog = json.loads(http_conn.getresponse().read())
        http_conn.close()

        # get peers from catalog
        now = time.time()
        all_peers = [entry for entry in catalog if entry.get('type', '') == ENTRY_TYPE and (now - entry.get('lastheardfrom') < 60)]

        duplicates = {}
        for peer in all_peers:
            if peer['uuid'] in duplicates:
                duplicates[peer['uuid']].append(peer)
            else:
                duplicates[peer['uuid']] = [peer]

        peers = [max(dupes, key=lambda k: k['lastheardfrom']) for dupes in duplicates.values()]

        return peers
        
    # Connects self's socket to a live sPin peer
    def _lookup_peer(self):
        
        # Get catalog
        http_conn = http.client.HTTPConnection(CATALOG_SERVER)
        http_conn.request('GET', '/query.json')
        
        # Parse catalog
        catalog = json.loads(http_conn.getresponse().read())
        http_conn.close()
        
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
                        self.addr = entry['address']
                        self.port = entry['port']
                        return
                    except:
                        self.s.close()
        
        print('Failed to connect to a live peer')
        
        
    # Adds a file to the network
    def sPinADD(self, filepath):
        
        peers = self.get_peers()
        if not len(peers):
            print('error: no peers found')
            sys.exit(1)

        # generate object id
        uuid_component = str(uuid.uuid4())
        hash_component = self.get_digest(filepath)
        object_id = uuid_component + ':' + hash_component
        
        # figure out k
        k = math.ceil(len(peers) / K_DENOM)

        # figure out which peers to pin to
        pin_to = random.choices(peers, k=k)

        #print(pin_to)

        for peer in pin_to:
            try:
                with open(filepath, 'rb') as to_upload:
                    multipart = {'data': to_upload}                                                                                                                                                                 
                    resp = requests.post(f'''http://{peer['name']}:{peer['port']}/add/{object_id}''', files=multipart)
                    print(resp.status_code)
            except FileNotFoundError as file_err:
                if self.main: print(f'error: could not open file {filepath}')
                sys.exit(1)
            except requests.RequestException as req_err:
                if self.main: print(f'error: could not connect to peer')
                sys.exit(1)

        if self.main: print(object_id)
        return object_id
        
    # Gets the file associated with the given key
    def sPinGET(self, object_id, filepath):
        
        peers = self.get_peers()
        if not len(peers):
            if self.main: print('error: no peers found')
            sys.exit(1)

        # figure out a few to try
        to_try = random.sample(peers, k=len(peers))

        success = False

        for peer in to_try:
            print(peer)
            try:
                http_conn = http.client.HTTPConnection(peer['name'], peer['port']) # TODO: add timeout?
                http_conn.request('GET', f'/get/{object_id}')
                #resp = requests.get(f'''http://{peer['name']}:{peer['port']}/get/{object_id}''')
                # TODO error check
                response = http_conn.getresponse()
                if response.status == 200:
                    response_body = response.read()
                    try:
                        with open(filepath, 'wb') as to_save:
                            to_save.write(response_body)
                    except OSError as file_err:
                        if self.main: print(f'error: could not open or write to file {filepath}')
                        sys.exit(1)
                    success = True
                    break
                http_conn.close()

            except OSError as file_err:
                if self.main: print(f'error: could not connect to peer, trying next option')
                
            except http.client.HTTPException as http_err:
                if self.main: print(f'error: could not connect to peer, trying next option')

        if self.main: print('successfully retrieved file')
        return 0 if success else 1
        
        
    # Requests deletion of the file associated with the given key
    def sPinDEL(self, object_id):
        
        peers = self.get_peers()
        if not len(peers):
            if self.main: print('error: no peers found')
            sys.exit(1)
        
        # figure out k
        k = math.ceil(len(peers) / K_DENOM)

        # figure out which peers to request del from
        del_from = random.choices(peers, k=k)

        for peer in del_from:
            try:
                http_conn = http.client.HTTPConnection(peer['name'], peer['port']) # TODO: add timeout?
                http_conn.request('POST', f'/del/{object_id}')
                # TODO error check
                http_conn.close()
            except http.client.HTTPException as http_err:
                if self.main: print(f'error: could not connect to peer')
                sys.exit(1)

        if self.main: print('successfully requested file deletion')

    # helper to get hexdigest of a file
    def get_digest(self, filepath):

        hash = hashlib.sha256()

        try:
            with open(filepath, 'rb') as to_hash:
                while True:
                    chunk = to_hash.read(hash.block_size)
                    if not chunk:
                        break
                    hash.update(chunk)
        except FileNotFoundError as file_err:
            if self.main: print(f'error: could not open file {filepath}')
            sys.exit(1)
            
        return hash.hexdigest()
    
# CLI options
# ADD
# program add file
# GET
# program get object_id dst
# DEL
# program del object_id
if __name__ == '__main__':

    client = sPinClient(True)

    usage = f'''usage:
        {sys.argv[0]} add <filename> - add contents of <filename> to system, returning object id
        {sys.argv[0]} get <object id> <filename> - get data for <object id>, if present, saving to <filename>
        {sys.argv[0]} del <object id> - make a deletion request for <object id>
        {sys.argv[0]} help - display this message
        '''

    if len(sys.argv) not in (3, 4):
        print(usage)
    elif sys.argv[1].lower() == 'get' and len(sys.argv) != 4:
        print(usage)
    elif sys.argv[1].lower() == 'help':
        print(usage)
    else:

        # get all arguments into a form we can use
        op = sys.argv[1].lower()
        if op == 'add':
            filename = sys.argv[2]
        else:
            object_id = sys.argv[2]

        if op == 'get':
            filename = sys.argv[3]

        # TODO: sanity check object ids

        if op == 'add':
            client.sPinADD(filename)
        elif op == 'get':
            sys.exit(client.sPinGET(object_id, filename))
        else: # del
            client.sPinDEL(object_id)

        sys.exit(0)