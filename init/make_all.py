#!/bin/usr/env python3

# John Sullivan (jsulli28), Jozef Porubcin (jporubci)
# make_all.py

import sys
import init_files, init_peers

files_dir = 'files'
peers_dir = 'peers'
peer_name = 'peer'
num_peers = 3

if len(sys.argv) == 1:
    init_files.init_files(files_dir)
    init_peers.init_peers(peers_dir, peer_name, num_peers)

elif len(sys.argv) == 2 and sys.argv[1] == 'init_files':
    init_files.init_files(files_dir)

elif len(sys.argv) == 2 and sys.argv[1] == 'init_peers':
    init_peers.init_peers(peers_dir, peer_name, num_peers)
