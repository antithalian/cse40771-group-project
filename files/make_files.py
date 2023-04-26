#!/usr/bin/env python3

by = 'b_file_'
kb = 'kb_file_'
mb = 'mb_file_'

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
