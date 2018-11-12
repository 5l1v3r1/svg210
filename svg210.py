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
    
document = minidom.parse(svgfile)
