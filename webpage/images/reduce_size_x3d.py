#!/usr/bin/env python3
#
import sys
from vedo import precision
from vedo.utils import isInteger, isNumber

infile = sys.argv[1]
digits = 4
print('processing', infile)

newlines = []
with open(infile, 'r') as f:
    lines = f.readlines()
    for l in lines:
        ls = l.lstrip()
        content = ls.split()
        newls = ""
        for c in content:
            c2 = c.replace(',','')
            if isNumber(c2) and not isInteger(c2):
                newc = precision(float(c2), digits)
                if ',' in c:
                    newls += newc + ','
                else:
                    newls += newc + ' '
            else:
                newls += c + ' '

        newlines.append(newls.lstrip()+'\n')

with open(infile.replace(".x3d","_reduced.x3d"), 'w') as f:
    l = "".join(newlines)
    f.write(l)
    print("file saved as", infile.replace(".x3d","_reduced.x3d"))
