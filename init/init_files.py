#!/usr/bin/env python3

# John Sullivan (jsulli28), Jozef Porubcin (jporubci)
# init_files.py

import shutil
import os

def init_files(files_dir):

    shutil.rmtree(files_dir + '/', ignore_errors=True)
    os.mkdir(files_dir + '/')
    os.chdir(files_dir + '/')
    
    for i in range(200):
        with open(f'10MB_file_{i}', 'wb') as file:
            file.write(os.urandom(10_000_000))
    
    os.chdir('../')
