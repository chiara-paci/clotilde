#!/usr/bin/python

import sys


num=map(lambda x: int(x),sys.argv[1:])


tot=reduce(lambda x,y:x+y,num)

for n in num:
    print "%4d: %2.2f" % (n,100*float(n)/tot)
