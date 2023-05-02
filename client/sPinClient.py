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
CLIENT_STALENESS = 60 # client should assume nameserver record is stale if older than 1m
RETRIES = 3 # retry 3x for things like not being able to hear from the catalog server, etc
K_DENOM = 3 # denominator for determining k

class sPinClient:
    def __init__(self, verbose=False):
        self.verbose = verbose
        
    def get_peers(self):

        catalog = None

        for _ in range(RETRIES):

            try:
                resp = requests.get(f'http://{CATALOG_SERVER}/query.json')
                resp.raise_for_status() # raise an exception is bad response

                # good response, get the JSON
                catalog = resp.json()
                break # break the retry loop
            except Exception as err:
                if self.verbose: 
                    print(f'error: could not communicate with nameserver: {err}')

        # return early if getting peers failed
        if not catalog:
            return []

        # get peers from catalog
        now = time.time()
        all_peers = [entry for entry in catalog if entry.get('type', '') == ENTRY_TYPE and (now - entry.get('lastheardfrom') < CLIENT_STALENESS)]

        # deduplicate the peers, keeping only the latest entry for a uuid
        duplicates = {}
        for peer in all_peers:
            if peer['uuid'] in duplicates:
                duplicates[peer['uuid']].append(peer)
            else:
                duplicates[peer['uuid']] = [peer]
        peers = [max(dupes, key=lambda k: k['lastheardfrom']) for dupes in duplicates.values()]

        return peers 
        
    # Adds a file to the network
    def sPinADD(self, filepath):
        
        peers = self.get_peers()
        if not len(peers):
            if self.verbose:
                print('error: no peers found')
            return False # return early if no peers found

        # generate object id
        uuid_component = str(uuid.uuid4())
        hash_component = self.get_digest(filepath)
        object_id = uuid_component + ':' + hash_component
        
        # figure out k
        k = math.ceil(len(peers) / K_DENOM)

        # figure out which peers to pin to
        pin_to = random.choices(peers, k=k)

        # try to pin to all, retrying each as needed
        overall_success = []
        for peer in pin_to:
            for _ in range(RETRIES):
                try:
                    with open(filepath, 'rb') as to_upload:
                        multipart = {'data': to_upload}                                                                                                                                                                 
                        resp = requests.post(f'''http://{peer['name']}:{peer['port']}/add/{object_id}''', files=multipart)
                        resp.raise_for_status() # raise an exception if POST failed
                        overall_success.append(True)
                    break # leave this inner loop if we succeeded
                except FileNotFoundError as file_err:
                    if self.verbose: 
                        print(f'error: could not open file {filepath}: {file_err}')
                    return False
                except requests.RequestException as req_err:
                    if self.verbose: 
                        print(f'error: could not connect to peer: {req_err}')
        
        # if all of those succeeded, return object id
        if all(overall_success):
            return object_id
        else:
            return False
        
    # Gets the file associated with the given key
    def sPinGET(self, object_id, filepath):

        peers = self.get_peers()
        if not len(peers):
            if self.verbose:
                print('error: no peers found')
            return False # return early if no peers found

        # get hash component of object id
        object_hash = object_id.split(':')[1]

        # figure out a few to try
        to_try = random.sample(peers, k=len(peers))

        success = False
        # no retries here, we're trying every peer
        for peer in to_try:
            try:
                resp = requests.get(f'''http://{peer['name']}:{peer['port']}/get/{object_id}''')
                resp.raise_for_status() # raise error if bad result

                # try to write to file
                # implement a streaming hash check at the same time
                with open(filename, 'wb') as file:
                    hash = hashlib.sha256()
                    for chunk in resp.iter_content(chunk_size=hash.block_size):
                        hash.update(chunk)
                        file.write(chunk)

                # check that hashes are same, if not, unlink file
                if object_hash != hash.hexdigest():
                    if self.verbose:
                        print(f'error: retrieved data hash of {hash.hexdigest()} did not match object hash of {object_hash}')
                    os.unlink(filename)
                    return False
                else:
                    success = True
                    break
            except requests.RequestException as req_err:
                if self.verbose:
                    print(f'error: could not retrieve object from peer, trying next if possible')
            except OSError as file_err:
                if self.verbose: 
                    print(f'error: could not write to file: {file_err}')
                return False

        return success
        
        
    # Requests deletion of the file associated with the given key
    def sPinDEL(self, object_id):
        
        peers = self.get_peers()
        if not len(peers):
            if self.verbose:
                print('error: no peers found')
            return False # return early if no peers found
        
        # figure out k
        k = math.ceil(len(peers) / K_DENOM)

        # figure out which peers to request del from
        del_from = random.choices(peers, k=k)

        # try to delete from all, retrying each as needed
        success = False
        for peer in del_from:
            for _ in range(RETRIES):
                try:
                    resp = requests.post(f'''http://{peer['name']}:{peer['port']}/del/{object_id}''')
                    resp.raise_for_status() # raise an exception if POST failed
                    overall_success = True
                    break # leave this inner loop if we succeeded
                except requests.RequestException as req_err:
                    if self.verbose: 
                        print(f'error: could not connect to peer: {req_err}')
        
        return overall_success

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

    client = sPinClient(verbose=True)

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

        filename, object_id = None, None

        # get all arguments into a form we can use
        op = sys.argv[1].lower()
        if op == 'add':
            filename = sys.argv[2]
        else:
            object_id = sys.argv[2]

        if op == 'get':
            filename = sys.argv[3]

        if object_id:
            try:
                object_uuid, object_hash = object_id.split(':')
                assert len(object_hash) == 64
                assert str(uuid.UUID(object_uuid)) == object_uuid
            except (ValueError, AssertionError):
                print(f'invalid object id {object_uuid}')

        exit_code = 0

        if op == 'add':
            result = client.sPinADD(filename)
            if result:
                print(result) # it's the object id
            else:
                print(f'failed to add file {filename}')
                exit_code = 1
        elif op == 'get':
            result = client.sPinGET(object_id, filename)
            if result:
                print(f'successfully saved {object_id} to {filename}')
            else:
                print(f'failed to get object {object_id}')
                exit_code = 1
        else: # del
            result = client.sPinDEL(object_id)
            if result:
                print(f'successfully requested deletion of {object_id}')
            else:
                print(f'failed to request deletion of object {object_id}')
                exit_code = 1

        sys.exit(exit_code)