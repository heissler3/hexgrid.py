#!/usr/bin/env python3

# hexgrid.py
# create a printable grid of hexagons
# outputs to a postscript file

# Author: Henry Eissler
# Date: 6/6/2016

import sys
from optparse import Option, OptionParser
from pyx import *
from math import *

#   Units are centimeters because that is the default in PyX,
#   and I could see no good reason to change it
pg_width = 21.6     #   A4 paper
pg_height = 27.9
margin = .75        #   minimum margin
page = canvas.canvas()

rows = 0
cols = 0
maxrise = (pg_height - (margin*2)) / 2
maxside = (pg_width - (margin*2)) / 2
sine60 = round(sin(radians(60)), 3)

options = [
    Option("-w", "--width", dest="width", type="float",
            help="width of hexagon in centimeters"),
    Option("-r", "--rows", dest="rows", type="int",
            help="number of rows to print"),
    Option("-c", "--cols", dest="columns", type="int",
            help="number of columns to print"),
    Option("-o", dest="outfile", default="hexgrid",
            help="output filename"),
    Option("-d", dest="debug", action="store_true", default=False,
            help="output stats")
    ]
optparser = OptionParser(option_list=options)
(clopts, args) = optparser.parse_args()

if clopts.width:                            #   A defined width takes precedence
    dy = clopts.width / 2
    side = dy / sine60
    dx = side / 2
    if clopts.rows:
        rows = clopts.rows
        if (rows * (dy * 2) + dy > pg_height - (margin*2)):
            print("Error: too large to fit on page", file=sys.stderr)
            exit(1)
    if clopts.columns:
        cols = clopts.columns
        if (cols * (side + dx) + dx > pg_width - (margin*2)):
            print("Error: too large to fit on page", file=sys.stderr)
            exit(1)
elif clopts.rows or clopts.columns:         #   Else, derive width from given row or column count
    if clopts.rows:
        rows = clopts.rows
        maxrise = (pg_height - (margin*2)) / ((rows * 2) + 1)
    if clopts.columns:
        cols = clopts.columns
        maxside = ((pg_width - (margin*2)) / ((cols * 3) + 1)) * 2
    if maxside < maxrise / sine60:
        side = maxside
        dx = side / 2
        dy = side * sine60
    else:
        dy = maxrise
        side = dy / sine60
        dx = side / 2
else:                                       #   Else, use defaults
    side = .577                             # (renders a width of 1cm)
    dx = side / 2
    dy = side * sine60

#   If rows or columns haven't been declared, derive them.
if not rows:
    rows = int((pg_height - (margin*2)) / (2 * dy))
if not cols:
    cols = int((pg_width - (margin*2) - dx) / (side + dx))

#   Is there enough room for alternating columns?
#   Or will every other one have one less row?
if pg_height - (margin*2) - (rows * 2 * dy) >= (dy - .001):     # (compensating for rounding errors)
    starty = (pg_height - (rows * dy * 2) - dy) / 2
    offset = 1
else:
    starty = (pg_height - (rows * dy * 2)) / 2
    offset = 0

x = ((pg_width - (cols * (side + dx)) - dx) / 2) + dx           # used to be a variable named 'startx'...
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if clopts.debug:
    print("rows:  {:2d}\t\tcols:  {:2d}".format(rows, cols), file=sys.stderr)
    print("side:  {:.3f}\t\twidth:  {:.3f}".format(side, side*sine60*2), file=sys.stderr)
    print("bottom margin:  {:.3f}\tleft margin:  {:.3f}".format(starty, x - dx), file=sys.stderr)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#   This is the "fast and dirty" way to do it.
#   Also the "sloppy and wasteful" way,
#   because many, many lines are redrawn over previous lines.
for c in range(cols):
    y = starty + offset * dy
    r = 0
    while (r < rows) and (y + (dy*2) <= (pg_height - margin)):
        hexagram = path.path(path.moveto(x, y),
                        path.rlineto(side, 0), path.rlineto(dx, dy), path.rlineto(-dx, dy),
                        path.rlineto(-side, 0), path.rlineto(-dx, -dy), path.rlineto(dx, -dy))
        page.stroke(hexagram)
        y += 2 * dy
        r += 1
    x += side + dx
    offset = 1 - offset     # toggle 0/1

page.writePSfile(clopts.outfile)
