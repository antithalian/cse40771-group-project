#!/usr/bin/env python3

# John Sullivan (jsulli28), Jozef Porubcin (jporubci)
# init_files.py

import shutil
import os, sys

def init_files(files_dir, file_size):

    shutil.rmtree(files_dir + '/', ignore_errors=True)
    os.mkdir(files_dir + '/')
    os.chdir(files_dir + '/')
    
    for i in range(200):
        with open(f'file_{i}', 'wb') as file:
            file.write(os.urandom(file_size))
    
    os.chdir('../')

if __name__ == '__main__':
    init_files('files', int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000)