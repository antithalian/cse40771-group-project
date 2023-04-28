#!/usr/bin/env python3

import math
import uuid
import random
import pin_funcs

num_peers = 9
k = math.ceil(num_peers / 3)

# Create 9 peer names
peers = set()
for _ in range(num_peers):
    peers.add(str(uuid.uuid4()))

# Create 3 file names
files = set()
for _ in range(k):
    files.add(str(uuid.uuid4()))

l = list(files)
pins = dict()

# There are 3 files, 9 peers. Each file should have 3 pins. File l[0] has too many pins (4). File l[-1] only too few pins (2).
for f in l:
    pins[f] = set()
    while len(pins[f]) < k:
        pins[f].add(random.choice(list(peers)))

while len(pins[l[0]]) < k+1:
    pins[l[0]].add(random.choice(list(peers)))

pins[l[-1]].remove(random.choice(list(pins[l[-1]])))

for f in pins:
    print(f'File name {f} has {len(pins[f])} pins')
    print('Pins:')
    for pin in pins[f]:
        print(pin)
    print()

for f in pins:
    while len(pins[f]) > k:
        drop_pin = None
        for pin in pins[f]:
            print(f'Calling pin: {pin}')
            print(f'Pins for file {f}:')
            for p in pins[f]:
                print(p)
            print()
            drop = pin_funcs.drop_pin(pin, pins[f])
            if drop:
                drop_pin = drop
            print(f'New pin: {drop_pin}')
            print()
        
        pins[f].remove(drop_pin)
        
    while len(pins[f]) < k:
        new_pin = None
        for pin in pins[f]:
            print(f'Calling pin: {pin}')
            print(f'Pins for file {f}:')
            for p in pins[f]:
                print(p)
            print('Not pins:')
            for peer in peers.difference(pins[f]):
                print(peer)
            print()
            add = pin_funcs.add_pin(pin, pins[f], peers.difference(pins[f]))
            if add:
                new_pin = add
            print(f'New pin: {new_pin}')
            print()
            
        pins[f].add(new_pin)

print('RESULTS')
for f in pins:
    print(f'File name {f} has {len(pins[f])} pins')
    print('Pins:')
    for pin in pins[f]:
        print(pin)
    print()
