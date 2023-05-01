#!/bin/usr/env python3

# John Sullivan (jsulli28), Jozef Porubcin (jporubci)
# ckpt.py

import os

# temp file extension
TEMP_EXTENSION = '.new'
CKPT_EXTENSION = '.ckpt'
LOG_EXTENSION = '.log'

# log entries are gonna be for tables holding insertions and deletions
# so prepend each line with add or del or something as needed

# Appends a transaction on a single line
# Automatically adds a new line character
def write_log(dir_path, log_name, data):
    log_file = open(dir_path + log_name, 'a')
    print(data, file=log_file, flush=True)
    os.fsync(log_file.fileno())
    log_file.close()
    
    
# Makes checkpoint and optionally clears log
# Only effective if transactions are idempotent
def write_ckpt(dir_path, ckpt_name, data, log_name=None):
    shadow_copy = open(dir_path + '.' + ckpt_name, 'w')
    print(data, end='', file=shadow_copy, flush=True)
    os.fsync(shadow_copy.fileno())
    shadow_copy.close()
    os.rename(dir_path + '.' + ckpt_name, dir_path + ckpt_name)
    os.remove(dir_path + '.' + ckpt_name)
    
    if log_name:
        log_file = open(dir_path + log_name, 'w')
        print('', end='', file=log_file, flush=True)
        os.fsync(log_file.fileno())
        log_file.close()

# load checkpoint from file, replaying as needed
def load_ckpt(dir_path, ckpt_name, log_name=None):
    pass
