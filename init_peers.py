#!/usr/bin/env python3

# John Sullivan (jsulli28), Jozef Porubcin (jporubci)
# init_peers.py

import shutil
import os
import sys

# Initializes peered server directory structure
def init_peers(name, n):
    shutil.rmtree(name + '/', ignore_errors=True)
    
    os.mkdir(name + '/')
    os.chdir(name + '/')
    for i in range(n):
        os.mkdir(name + str(i) + '/')
        os.chdir(name + str(i) + '/')
        os.mkdir('pins/')
        os.mkdir('cache/')
        os.mkdir('meta/')
        os.chdir('meta/')
        os.mkdir('name/')
        os.mkdir('checkpoints/')
        os.chdir('../')
        os.chdir('../')
    
    
if len(sys.argv) == 3:
    init_peers(sys.argv[1], int(sys.argv[2]))
