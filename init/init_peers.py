#!/usr/bin/env python3

# John Sullivan (jsulli28), Jozef Porubcin (jporubci)
# init_peers.py

import shutil
import os
import uuid
import json

# Initializes peered server directory structure
def init_peers(peers_dir, peer_name, num_peers):
    shutil.rmtree(peers_dir + '/', ignore_errors=True)
    
    os.mkdir(peers_dir + '/')
    os.chdir(peers_dir + '/')
    for _ in range(num_peers):
        peer_name = str(uuid.uuid4())
        os.mkdir(peer_name + '/')
        os.chdir(peer_name + '/')
        # add server files
        server_files = os.listdir('../../server')
        for file in server_files:
            shutil.copy(os.path.join('../../server/', file), '.')
        os.mkdir('pinned_files/')
        os.mkdir('cached_files/')
        os.mkdir('meta/')
        os.chdir('meta/')
        n = open('name', 'x')
        print(peer_name, file=n)
        n.close()
        c = open('deletes.ckpt', 'x')
        print(json.dumps(list()), end='', file=c)
        c.close()
        l = open('deletes.log', 'x')
        l.close()
        os.chdir('../')
        os.chdir('../')
