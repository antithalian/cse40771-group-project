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
        os.mkdir('pinned_files/')
        os.mkdir('cached_files/')
        os.mkdir('meta/')
        os.chdir('meta/')
        f = open('deletes.ckpt', 'x')
        print(json.dumps(list()), end='', file=f)
        f.close()
        fd = os.open('deletes.log', os.O_CREAT | os.O_EXCL)
        os.close(fd)
        os.chdir('../')
        os.chdir('../')
