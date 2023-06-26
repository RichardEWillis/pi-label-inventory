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

# if True, existing pdf files will be over-written, if set False the existing
# PDF file will be kept and the new printed labels added to it.
OVERWRITE_EXISTING_PDF = True

VER = "1.0b BETA"

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
        fsqwgt = f"{fullseq:<7} {weight:>6}"
        descstr = obj['desc']
        label.add( shapes.String(4, 42, descstr, fontName="Helvetica", fontSize=20) )
        label.add( shapes.String(2, 4, fsqwgt, fontName="Helvetica", fontSize=34) )
    except:
        pass

def render_label(sheet, seqnum, desc, weight):
    sheet.add_label( {"sn":seqnum, "desc":desc, "wgt":weight} )

# This method is run by default and forms an interactive menu based system for 
# editing inventory database and printing labels
def main_loop():

    # Menu Options
    menu_title = "Package Inventory and Label Generator Ver %s" % VER
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
                    print("[%03d] sn = %03d weight = %s desc: %s" % (int(i), int(sn), wgt, desc) )

                input("Hit a key to continue")
                continue

            if sel == OBJ_ADD:
                sn = int(1 + db.Size())
                wgt = 0
                desc = ""
                while True:
                    print("Serial: %03d" % sn)
                    wgt = input("Weight: ")
                    desc = input("Description: ")
                    getok = input("sn[%03d] weight[%s] [%s] - Accept? (Y/N) [Y]" % (sn, wgt, desc))
                    if getok == "" or getok == "Y" or getok == "y":
                        break
                    else:
                        clear_screen()
                db.Append( ivdbase.recGen(sn, desc, wgt) )
                continue

            if sel == OBJ_REPL:
                while True:
                    isn = int( input("SerialNum to Edit? : ") )
                    oidx = db.IndexOfSN(isn)
                    if oidx >= 0:
                        (foo, desc, wgt) = ivdbase.recDec( db.Read(oidx) )
                        iwgt = input("Weight [%s]: " % wgt)
                        if iwgt == "":
                            iwgt = wgt
                        idesc = input("Description [%s]: " % desc)
                        if idesc == "":
                            idesc = desc
                        getok = input("sn[%03d] weight[%s] [%s] - Accept? (Y/N) [Y]" % (isn, iwgt, idesc))
                        if getok == "" or getok == "Y" or getok == "y":
                            break
                    else:
                        print("serial number not found")
                        input("Hit a key to continue")
                rc = db.Replace(oidx, ivdbase.recGen(isn, idesc, iwgt) )
                if rc == 0:
                    print("Index %s updated." % isn)
                else:
                    print("Error occured duing dbase edit.")
                input("Hit a key to continue")
                continue

            if sel == PRINT_LABELS:
                if db.Size() == 0:
                    input("No inventory in memory, press Enter to continue.")
                    continue
                start_val = 0
                end_val = 0
                while True:
                    styp = input("Search by (I)ndex or (S)erialNumber (I/S) [I] ? : ")
                    if styp == "" or styp[0] == 'I' or styp[0] == 'i':
                        stype = "IDX"
                        start_val = input("Select Start Index for print [0] :")
                        if start_val == "":
                            start_val = 0
                        else:
                            start_val = int(start_val)
                        e_val = db.Size() - 1
                        end_val = input("Select Last Index to print [%d] :" % e_val)
                        if end_val == "":
                            end_val = e_val
                        else:
                            end_val = int(end_val)
                        print("Printing from Index [%d] to Index [%d]" % (start_val, end_val))
                    else:
                        stype = "SN"
                        start_val = input("Select Starting SerialNum for print [1] :")
                        if start_val == "":
                            start_val = 1
                        else:
                            start_val = int(start_val)
                        e_obj = db.Read( db.Size() - 1 )
                        e_val = int( e_obj['sn'] )
                        end_val = input("Select Last SerialNum to print [%d] :" % e_val)
                        if end_val == "":
                            end_val = e_val
                        else:
                            end_val = int(end_val)
                        if end_val > e_val:
                            input("Ending SerialNum out of range (too high). Hit return to re-enter.")
                            continue # while-True
                        print("Printing from SN [%d] to SN [%d]" % (start_val, end_val))
                        # convert to indexes, for printing.
                        start_val = db.IndexOfSN(start_val)
                        end_val = db.IndexOfSN(end_val)
                    break                
                # exit while-loop, everything converted to indexes.
                for i in range(start_val, end_val+1):
                    (snval, descval, wgtval) = ivdbase.recDec( db.Read(i) )
                    render_label(sheet, seqnum=int(snval), desc=descval, weight=wgtval)
                if filename == "":
                    filename = input("Enter a filename to save the generated labels to (PDF)")
                finput = filename.split('.') # pop off any possible suffix and replace with a .pdf
                labelfile = finput[0] + '.pdf'
                if OVERWRITE_EXISTING_PDF:
                    #check if exists and then delete existing - option
                    if os.path.isfile(labelfile):
                        os.remove(labelfile)
                sheet.save(labelfile)
                input("PDF document %s saved to file. Press any key to continue." % labelfile)
                continue

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
