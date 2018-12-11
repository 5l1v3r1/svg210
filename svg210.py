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
        
#print(gradientColorLists)
#print(gradientInstances)

groups = root.getElementsByTagName('g')

# Specify format
endian = '<' # little endian
datatype = 'H' # unsigned short
fmt = endian + datatype

# Pack texture
# Number of groups is not packed. This should be 1. If not, fix your svg.
group = groups[0]

# Pack number of paths 
paths = group.getElementsByTagName('path')
texture = struct.pack(fmt, len(paths))
print("Packing ", len(paths), "paths.")

# Identify global transform
# This is assumed to be only a translation. If it is not, fix your
# SVG.
transform = group.getAttribute("transform")
transform = transform.lstrip("translate(").rstrip(")").split(',')
transform = [ float(l) for l in transform ]

# Pack actual paths
fillcolors = []
for path in paths:
    # Set sensible defaults in case keys are not present
    fillcolor = [0.,0.,0.]
    fillopacity = 1.
    strokecolor = [0.,0.,0.]
    strokeopacity = 1.
    strokewidth = 0.

    # Get style
    style = path.getAttribute('style')
    entries = style.strip().split(';')
    for entry in entries:
        pair = entry.split(':')
        key = pair[0]
        value = pair[1]
        
        # Update information
        if key == 'fill':
            fillcolor = [ float(int(value[1:3], 16))/255., float(int(value[3:5], 16))/255., float(int(value[5:], 16))/255. ]
        elif key == 'fill-opacity':
            fillopacity = float(value)
        elif key == 'stroke':
            strokecolor = [ float(int(value[1:3], 16))/255., float(int(value[3:5], 16))/255., float(int(value[5:], 16))/255. ]
        elif key == 'stroke-width':
            strokewidth = float(value.replace('px',''))
        elif key == 'stroke-opacity':
            strokeopacity = float(value)
    
    # Get spline control data
    control = path.getAttribute('d')
    data = control.split()
    lin = []
    cub = []
    pos = transform
    print(data)
    for i in range(len(data)):
        datum = data[i]
        print(data[i])
        if datum == 'm':
            i += 1
            delta = [ float(l) for l in data[i].split(',') ]
            for j in range(2):
                pos[j] = pos[j] + delta[j]
            continue
        if datum == 'c':
            i += 1
            print('>',data[i])
            # First point
            cub += [ pos ]
            delta = [ float(l) for l in data[i].split(',') ]
            for j in range(2):
                pos[j] = pos[j] + delta[j]
            i += 1
            print('>>',data[i])
            # Second point
            cub += [ pos ]
            
            delta = [ float(l) for l in data[i].split(',') ]
            for j in range(2):
                pos[j] = pos[j] + delta[j]
            i += 1
            print('>>>',data[i])
            # Third point
            cub += [ pos ]
            delta = [ float(l) for l in data[i].split(',') ]
            for j in range(2):
                pos[j] = pos[j] + delta[j]
            i += 1
            
            # Last point
            cub += [ pos ]
            delta = [ float(l) for l in data[i].split(',') ]
            for j in range(2):
                pos[j] = pos[j] + delta[j]

            continue
        
        if datum == 'l':
            i += 1
            
            # First point
            lin += [ pos ]
            delta = [ float(l) for l in data[i].split(',') ]
            for j in range(2):
                pos[j] = pos[j] + delta[j]
            i += 1
            
            # Second point
            lin += [ pos ]
            delta = [ float(l) for l in data[i].split(',') ]
            for j in range(2):
                pos[j] = pos[j] + delta[j]

            continue
            
    # Add linear control data
    text = "vec2 lin["+str(len(lin))+"]=vec2["+str(len(lin))+"]("
    for l in lin:
        text += "vec2("+str(l[0])+","+str(l[1])+"),"
    if len(text) > 0:
        text = text[:-1]+");"
    print(text)
    
    # Add cubic control data
    text = "vec2 cub["+str(len(cub))+"]=vec2["+str(len(cub))+"]("
    for l in cub:
        text += "vec2("+str(l[0])+","+str(l[1])+"),"
    if len(text) > 0:
        text = text[:-1]+");"
    print(text)
    
    print("==============")
    
    
    

# Get circles
circles = group.getElementsByTagName('circle')
print(len(circles))
for circle in circles:
    print("circle", circle)
    
# Get Ellipses
ellipses = group.getElementsByTagName('ellipse')
for ellipse in ellipses:
    print("ellipse", ellipse)

