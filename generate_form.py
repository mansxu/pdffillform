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

# generate_form:
#   python script to generate a fillable PDF form from image or PDF
#   requires: ImageMagick, scribus, python, and their dependencies

# 0. utility functions
import sys
import subprocess
import tempfile

def usage():
    print sys.argv[0] + " input.ext form.pdf"
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
    
# 1. check arguments
if len(sys.argv) < 2:
    usage()
imagefile = sys.argv[1]
formfile = sys.argv[2]

# 2. convert imagefile to format suitable to scribus    
tmpfilename = tmpfile(".png")
out = subprocess.check_output(["convert", "-density", "300", "-background", "white", imagefile, tmpfilename])

exit()

# 3. start scribus with a script as argument to generate a new document and add the tmpfile as an image (not possible with Scribus 1.4)
script = "import sys, scribus \n\
def main(argv): \n\
    sayhello='idontknow' \n\
    i = 1; \n\
    while i < len(argv): \n\
        if argv[i] == 'hello': \n\
            sayhello='yes' \n\
            print 'hello world' \n\
        i = i + 1 \n\
    if sayhello=='idontknow': \n\
        print 'Sorry i wasnt asked to say Hello' \n\
    print 'good bye' \n\
if __name__ == '__main__': \n\
    main(sys.argv)"
sf = tmpfile(".py")
print sf
tf = open(sf, "w")
tf.write(script)
tf.close()
subprocess.check_output(["scribus", "-py", sf, "-pa", "imagefile", tmpfilename])
                         
                        
