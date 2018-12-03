# svg210 - convert svg to c texture content
# Copyright (C) 2017/2018 Alexander Kraus <nr4@z10.info>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import argparse
from xml.dom import minidom
import struct

parser = argparse.ArgumentParser(description='Memory Texture SVG Generation Tool by Team210.')
parser.add_argument('-s', '--svgfile', dest='svgfile')
parser.add_argument('-o', '--output', dest='outfile')
args, rest = parser.parse_known_args()

write_file = True
if args.svgfile == None:
    print("No SVG file specified. Doing nothing.")
    exit()
if args.outfile == None:
    print("No output file selected. Writing to stdout instead.")
    write_file = False
    
document = minidom.parse(args.svgfile)
root = document.getElementsByTagName("svg")[0]

defs = root.getElementsByTagName("defs")[0]

# Get gradients
gradients = defs.getElementsByTagName("linearGradient")
gradientColorLists = []
gradientInstances = []
for gradient in gradients:
    id = gradient.getAttribute("id")
    print("Found gradient:",id)
    stops = gradient.getElementsByTagName("stop")
    if len(stops) == 0: # Gradient with relative definition
        # Generate transformation matrix from absolute coordinates first.
        transform = gradient.getAttribute('gradientTransform')
        transformMatrix = np.zeros((3,3))
        if transform[:len('translate')] == 'translate':
            print("translate")
            transform = transform.lstrip('translate(').rstrip(')')
            coords = transform.split(',')
            transformList = [ [1, 0, float(coords[0])], [0, 1, float(coords[1])], [0,0,1] ]
            transformMatrix = np.matrix(transformList)
        elif transform[:len('matrix')] == 'matrix':
            print("matrix")
            transform = transform.lstrip('matrix(').rstrip(')')
            coords = transform.split(',')
            transformList = [ [float(coords[2*i]) for i in range(3)], [float(coords[2*i+1]) for i in range(3)], [0, 0, 1] ]
            transformMatrix = np.matrix(transformList)
        elif transform == '':
            print("nothing.")
        print(transformMatrix)
        
        # Get control points.
        p1 = [ float(gradient.getAttribute('x1')), float(gradient.getAttribute('y1')) ]
        p2 = [ float(gradient.getAttribute('x2')), float(gradient.getAttribute('y2')) ]
        print("control points",p1,p2)
        links = gradient.getAttribute('xlink:href').lstrip('#')
        print("links:", links)
        
        gradientInstances += [ [id, links, transformMatrix, p1, p2] ]
    else:
        gradientColorList = []
        for stop in stops: # gradient with stops and with absolute definition 
            style = stop.getAttribute("style")
            style_css = style.split(';')
            rgb = ''
            a = ''
            for directive in style_css:
                nameValue = directive.split(':')
                
                if nameValue[0] == u'stop-color':
                    rgb = nameValue[1]
                elif nameValue[0] == u'stop-opacity':
                    a = nameValue[1]
            hexcolor = rgb.lstrip('#')
            hexvalues = [ float(int(hexcolor[2*i:2*(i+1)], 16))/255. for i in range(3) ]
            hexvalues += [ float(int(a,10)) ]
            gradientColorList += [ hexvalues ]
        gradientColorLists += [ [ id, gradientColorList] ]
        
print(gradientColorLists)
print(gradientInstances)

groups = root.getElementsByTagName('g')
for group in groups:
    # Get paths
    paths = group.getElementsByTagName('path')
    print(len(paths))
    for path in paths:
        print("path",path)
    
    # Get circles
    circles = group.getElementsByTagName('circle')
    print(len(circles))
    for circle in circles:
        print("circle", circle)
        
    # Get Ellipses
    ellipses = group.getElementsByTagName('ellipse')
    for ellipse in ellipses:
        print("ellipse", ellipse)
    
