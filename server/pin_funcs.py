#!/bin/usr/env python3

# John Sullivan (jsulli28), Jozef Porubcin (jporubci)
# pin_funcs.py

import random

# Takes in:
# 1) calling_pin: the calling pin's own name
# 2) pins:        the set of names of known pins for a given file (including self)
# 3) not_pins:    the set of names of known peers that aren't pins for a given file
# 
# If calling_pin is not min(pins), returns None
# Else, returns a random peer's name from not_pins
# 
# This function should be called when the number of known pins for a given file goes below some scalar multiple of the number of known peers.
# This function should be called only by a pin for a given file, because only a pin with the file will be able to send the file to a peer.
# This function does not check if the pin actually has the file, so check that before calling this function.
# 
# If this function returns a peer's name, the calling pin should update its pin information before sending the file (might be risky), or
# disallow asynchronous operations until the file is sent, received, and the pin information is updated afterwards (probably safer), because
# it could be problematic if the returned peer crashes before receiving the file.
def add_pin(calling_pin, pins, not_pins):
    if calling_pin != min(pins):
        return
    
    # I use random.choice just because I'm not sure *how* random iterating over a set in python is:
    # Like: (for peer in not_pins, and then just choose the first peer)
    l = list(not_pins)
    peer = random.choice(l)
    
    return peer
    
    
# Pin with the highest name randomly chooses a pin to drop.
# Returns the name of the pin that should delete their file.
def drop_pin(calling_pin, pins):
    if calling_pin != max(pins):
        return
    
    l = list(pins)
    pin = random.choice(l)
    
    return pin
