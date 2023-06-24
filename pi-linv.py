# This file is part of pylabels, a Python library to create PDFs for printing
# labels.
# Copyright (C) 2012, 2013, 2014 Blair Bonnett
#
# pylabels is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pylabels is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# pylabels.  If not, see <http://www.gnu.org/licenses/>.

#import sys
#sys.path.insert(0, "/home/rwillis/git/pylabels")

import labels
from reportlab.graphics import shapes

# Create an A4 portrait (210mm x 297mm) sheets with 2 columns and 8 rows of
# labels. Each label is 90mm x 25mm with a 2mm rounded corner. The margins are
# automatically calculated.
# specs = labels.Specification(210, 297, 2, 8, 90, 25, corner_radius=2)
specs = labels.Specification(sheet_width=210, sheet_height=297, columns=2, 
                             rows=8, label_width=90, label_height=25, 
                             corner_radius=2 )
# Create a function to draw each label. This will be given the ReportLab drawing
# object to draw on, the dimensions (NB. these will be in points, the unit
# ReportLab uses) of the label, and the object to render.
# obj := {sn=1, desc='stuff', wgt=10}
def draw_label(label, width, height, obj):
    # +--------------------------+
    # | Description              |
    # | REW-xxx            (lbs) |
    # +--------------------------+
    
    if type(obj).__name__ != 'dict':
        bt = print( type(obj).__name__ )
        raise Exception('label function did not receive an object of type dict (%s)' % bt)
    try:
        seq = sval=f"{obj['sn']}".zfill(3)
        fullseq = f"REW-{seq}"
        weight = obj['wgt']
        fsqwgt = f"{fullseq} {weight}"
        descstr = obj['desc']
        label.add( shapes.String(4, 42, descstr, fontName="Helvetica", fontSize=20) )
        label.add( shapes.String(2, 4, fsqwgt, fontName="Helvetica", fontSize=36) )
    except:
        pass

def render_label(sheet, seqnum, desc, weight):
    sheet.add_label( {"sn":seqnum, "desc":desc, "wgt":weight} )

# Create the sheet.
sheet = labels.Sheet(specs, draw_label, border=True)

# Add a couple of labels.
# sheet.add_label("Hello")
# sheet.add_label("World")
render_label(sheet, seqnum=1, desc="First Label", weight=10.5)
render_label(sheet, seqnum=2, desc="Second Label", weight=32.1)

# We can also add each item from an iterable.
# sheet.add_labels(range(3, 16))

# Note that any oversize label is automatically trimmed to prevent it messing up
# other labels.
# sheet.add_label("Oversized label here")

# Save the file and we are done.
sheet.save('basic2.pdf')
print("{0:d} label(s) output on {1:d} page(s).".format(sheet.label_count, sheet.page_count))
