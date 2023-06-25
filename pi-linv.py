# This file is part of py-linv, for managing moving packages and calculating 
# weight.
# Copyright (C) 2023, Richard Willis
#
# py-linv is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# py-linv is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#

import labels
import os
from reportlab.graphics import shapes
from simple_term_menu import TerminalMenu
from ivdbase_class import ivdbase

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

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

# This method is run by default and forms an interactive menu based system for 
# editing inventory database and printing labels
def main_loop():

    # Menu Options
    menu_title = "Package Inventory and Label Generator Ver 0.01 (ALPHA-UNSTABLE)"
    options = ["[o] Open Inventory CSV File", 
               "[s] Save Inventory CSV File", 
               "[l] List Inventory", 
               "[a] Add Parcel", 
               "[e] Edit Parcel", 
               "[p] Generate Labels", 
               "[x] Exit" ]

    INV_FILE_READ = 0
    INV_FILE_WRITE = 1
    INV_LIST = 2
    OBJ_ADD = 3
    OBJ_REPL = 4
    PRINT_LABELS = 5
    MENU_EXIT = 6

    # Create an A4 portrait (210mm x 297mm) sheets with 2 columns and 8 rows of
    # labels. Each label is 90mm x 25mm with a 2mm rounded corner. The margins are
    # automatically calculated.
    specs = labels.Specification(sheet_width=210, sheet_height=297, columns=2, 
                                rows=8, label_width=90, label_height=25, 
                                corner_radius=2 )

    # Create the sheet.
    sheet = labels.Sheet(specs, draw_label, border=True)

    tmenu = TerminalMenu(menu_entries=options, 
                         title=menu_title,
                         cycle_cursor=True,
                         clear_screen=True)

    # Inventory Database
    db = ivdbase()
    filename = ""

    run_loop = True

    while run_loop:
        sel = tmenu.show()
        if db.Size() == 0:
            print("No Records")
        else:
            print("Record Count: %s" % db.Size())

        if sel != None:
            print("Selected: %s" % options[sel])
            if sel == INV_FILE_READ:
                filename = input("Enter filename to load: ")
                reccount = db.Load(filename)
                if reccount < 0:
                    print("File not found, nothing loaded.")
                    input("Hit a key to continue")
                    continue

            if sel == INV_FILE_WRITE:
                if filename != "":
                    print("Loaded File: {%s}" % filename)
                fname = input("Enter filename to save, or hit ENTER to overwrite loaded file: ")
                if fname == "" and filename == "":
                    print("No loaded file, you must enter a new filename to save to")
                    input("Hit a key to continue")
                    continue
                if fname != "":
                    filename = fname
                reccount = db.Save(filename)
                print("File saved.")
                input("Hit a key to continue")
                continue

            if sel == INV_LIST:
                len = db.Size()
                for i in range(len):
                    (sn, desc, wgt) = ivdbase.recDec( db.Read(i) )
                    print("[%03d] sn = %03d weight = %03d desc: %s" % (int(i), int(sn), int(wgt), desc) )

                input("Hit a key to continue")
                continue

            if sel == OBJ_ADD:
                sn = 1 + db.Size()
                wgt = 0
                desc = ""
                while True:
                    print("Serial: %03d" % sn)
                    wgt = input("Weight: ")
                    desc = input("Description: ")
                    getok = input("sn[%03d] weight[%03d] [%s] - Accept? (Y/N) [Y]")
                    if getok == "" or getok == "Y" or getok == "y":
                        break
                    else:
                        clear_screen()
                db.Append( ivdbase.recGen(sn, desc, wgt) )
                continue

            if sel == OBJ_REPL:
                pass
            if sel == PRINT_LABELS:
                pass


            if sel != MENU_EXIT:
                # block here for a bit so the selection shows up.
                input("Hit a key to continue")

        if sel == MENU_EXIT or sel == None:
            run_loop = False

    print("Exited.")









## Add a couple of labels.
## sheet.add_label("Hello")
## sheet.add_label("World")
#render_label(sheet, seqnum=1, desc="First Label", weight=10.5)
#render_label(sheet, seqnum=2, desc="Second Label", weight=32.1)
#
## We can also add each item from an iterable.
## sheet.add_labels(range(3, 16))
#
## Note that any oversize label is automatically trimmed to prevent it messing up
## other labels.
## sheet.add_label("Oversized label here")
#
## Save the file and we are done.
#sheet.save('basic2.pdf')
#print("{0:d} label(s) output on {1:d} page(s).".format(sheet.label_count, sheet.page_count))



if __name__ == "__main__":
    main_loop()
