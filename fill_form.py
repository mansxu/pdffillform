#!/usr/bin/env python

# Copyright 2017 Marco R. Gazzetta (user mansxu on github) All rights reserved
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# fill_form
#   python script to fill out a generated PDF form from data
#   requires: Python, pdftk

# Data files are simple key=value pairs. Any string is available for key if 
#     it doesn't contain an = sign. Any string is available for value but can't span
#     lines (\n may be used)
# the special keywords 'alias' and 'split' are used to indicate redirection
#     alias NAME=FORM1 FORM2 FORM10
# means that the keys FORM1 FORM2 and FORM10 will be assigned the values of NAME
#     split DAYTIME=mo/da/yyyy hh:mm:ss
# means that the key DAYTIME will have the value given by substituting the keys
# mo, da, yyyy, hh, mm, ss in the value - note that in this case, only upper
# and lower case characters and numbers are valid in keys, and they cannot be used 
# in the substitution string
#
# Data files are read in the order passed in and the keys in the order in the file
# aliases and splits are processed at the end. You can overwrite a key/value assignment
# in later files, but aliases and split are assigned in random order

# 0. utility functions
import re
import tempfile
import subprocess
import sys

def usage():
    print sys.argv[0] + " form.pdf output.pdf data1.txt [data2.txt ...]"
    exit(1)
    
def tmpfile(suffix = None):
    tf = tempfile.NamedTemporaryFile(suffix=suffix)
    if tf:
        tfn = tf.name
        tf.close()
        return tfn
    else:
        print "Could not create temporary file"
        exit()
        
def escaped(s):
    s = s.replace('\\', '\\\\')
    s = s.replace('(', '\\(')
    s = s.replace(')', '\\)')
    return s  
        
# 1. check arguments
if len(sys.argv) < 3:
    usage()
formfile = sys.argv[1]
outpfile = sys.argv[2]
datafiles = sys.argv[3:]

# 2. read data files and merge the data in sequence
data = {}
aliases = {}
splits = {}
for df in datafiles:
    with open(df, "r") as f:
        for line in f:
            key, value = line.split('=', 1)
            value = value.strip()
            l = key.split(' ', 1)
            if len(l) == 2:
                t, k = l
                if t == 'string':
                    key = k
                elif t == 'alias':
                    aliases[k] = value
                elif t == 'split':
                    splits[k] = value
            if key:
                data[key] = value
        for k in aliases.keys():
            for x in aliases[k].split():
                data[x] = data[k]
        for k in splits.keys():
            ms = re.findall("[A-Za-z0-9]+", splits[k])
            if ms:
                r = splits[k]
                for m in ms:
                    r = re.sub(m, data[m], r)
                data[k] = r

# 3. generate the FDF file from the form
ffname = tmpfile('.fdf')
newname = tmpfile('.fdf')
print "Generating FDF from form: [" + subprocess.check_output(["pdftk", formfile, "generate_fdf", "output", ffname]) + "]"
ff = open(ffname, 'r')
nf = open(newname, 'w')
with ff as f:
    line = ''
    for l in f:
        if not re.search('>>', l):
            line += l
            continue
        line += l
        re1 = "<<.*/V.*\((.*)\).*/T.*\((.*)\).*>>"
        match = re.search(re1, line, re.S)
        if match:
            k = match.group(2)
            if k in data.keys():
                v = escaped(data[k])
            else:
                v = ""
            line = line[:match.start(1)]+v+line[match.end(1):match.start(2)]+k+line[match.end(2):]
        nf.write(line)
        line = ''
    nf.write(line)

nf.close()
ff.close()

# 4. generate the PDF file from the previous
print"Generating PDF: [" + subprocess.check_output(["pdftk", formfile, "fill_form", newname, "output", outpfile]) + "]"