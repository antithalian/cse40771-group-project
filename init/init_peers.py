#!/usr/bin/env python3

# John Sullivan (jsulli28), Jozef Porubcin (jporubci)
# init_peers.py

import shutil
import os

# Initializes peered server directory structure
def init_peers(peers_dir, num_peers):
    shutil.rmtree(peers_dir + '/', ignore_errors=True)
    
    os.mkdir(peers_dir + '/')
    os.chdir(peers_dir + '/')
    for i in range(num_peers):
        os.mkdir(peers_dir + str(i) + '/')
        os.chdir(peers_dir + str(i) + '/')
        os.mkdir('pins/')
        os.mkdir('cache/')
        os.mkdir('meta/')
        os.chdir('meta/')
        os.mkdir('name/')
        os.mkdir('checkpoints/')
        os.chdir('../')
        os.chdir('../')
