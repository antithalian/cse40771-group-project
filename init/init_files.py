#!/usr/bin/env python3

# John Sullivan (jsulli28), Jozef Porubcin (jporubci)
# init_files.py

import shutil
import os

def init_files(files_dir):
    by = 'b_file_'
    kb = 'kb_file_'
    mb = 'mb_file_'

    shutil.rmtree(files_dir + '/', ignore_errors=True)
    os.mkdir(files_dir + '/')
    os.chdir(files_dir + '/')
    
    for i in range(4):
        a = open(by + str(i) + '.txt', 'x')
        b = open(kb + str(i) + '.txt', 'x')
        c = open(mb + str(i) + '.txt', 'x')
        
        a.write(str(i))
        for j in range(1<<10):
            b.write(str(i))
        for j in range(1<<20):
            c.write(str(i))
        
        a.close()
        b.close()
        c.close()
    
    os.chdir('../')
