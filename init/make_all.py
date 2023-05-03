#!/bin/usr/env python3

# John Sullivan (jsulli28), Jozef Porubcin (jporubci)
# make_all.py

import sys
import init_files, init_peers

files_dir = 'files'
peers_dir = 'peers'
peer_name = 'peer'
num_peers = 3
file_size = 10 * (1024 ** 2)

if len(sys.argv) == 1:
    init_files.init_files(files_dir)
    init_peers.init_peers(peers_dir, peer_name, num_peers)

elif len(sys.argv) == 2 and sys.argv[1] == 'init_files':
    init_files.init_files(files_dir, file_size)

elif len(sys.argv) == 3 and sys.argv[1] == 'init_files':
    init_files.init_files(files_dir, int(sys.argv[2]))

elif len(sys.argv) == 2 and sys.argv[1] == 'init_peers':
    init_peers.init_peers(peers_dir, peer_name, num_peers)

elif len(sys.argv) == 3 and sys.argv[1] == 'init_files':
    init_files.init_peers(peers_dir, peer_name, int(sys.argv[2]))