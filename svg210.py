import numpy as np
import argparse
from xml.dom import minidom

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

# Get paths
groups = root.getElementsByTagName('g')
for group in groups:
    paths = group.getElementsByTagName('path')
    for path in paths:
        continue
