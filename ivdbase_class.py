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

IVDBDEBUG = False

class ivdbase(object):

    """
    ivdbase-class.py
        Python class for managing a simple CSV based inventory including methods to
        add, read, load and save.

        dobj - record object, type='dict'
        dobj := { "sn", "desc", "wgt" }
          sn   := (serial number, unique) [int]
          desc := (package description) [string]
          wgt  := (package weight, lbs/kgs) [int]

        filename - record file's filename is not retained by this class.
        filename := <path>/<name>.csv
        filename - csv suffic will be added by the class if not in the string
    """

    # Encode discrete data parameters into a dict object
    def recGen(sn, desc, wgt):
        return {"sn":int(sn), "desc":desc, "wgt":wgt}

    # Decode discrete data parameters from a dict object
    def recDec(obj):
        return (obj["sn"], obj["desc"], obj["wgt"])

    # create CSV line from the discrete data parameters
    def lineGenDisc(sn,desc,wgt):
        return "%s, %s, %s\n" % (sn, desc, wgt)

    # create CSV line string directly from the dict object
    def lineGen(obj):
        (sn,desc,wgt) = ivdbase.recDec(obj)
        return ivdbase.lineGenDisc(sn,desc,wgt)

    # Decode discrete data parameters from a CSV line [string]
    def lineDec(line):
        line = line.rstrip()
        el = line.split(',')
        if len(el) >= 3:
            if IVDBDEBUG:
                print("{ivdbase.lineDec()} sn:%s, desc:%s, wgt:%s" % (el[0],el[1],el[2]) )
            return (el[0], el[1], el[2])
        else:
            return None

    def __init__(self):
        self.dblist = []
        self.dblen = 0

    def Reset(self):
        self.dblist = []
        self.dblen = 0

    def Size(self):
        return self.dblen
    
    # find the dbase index for the given serial number
    def IndexOfSN(self, sn):
        for i in range(self.dblen):
            #print(type(self.dblist[i]["sn"]).__name__)
            #print(type(sn).__name__)
            if self.dblist[i]["sn"] == int(sn):
                return i
        return -1 # not found

    #TODO: place a .csv at the end if not in the filename
    def Load(self, filename):
        self.dblist = []
        self.dblen = 0
        if not filename.endswith('.csv'):
            filename += '.csv'
        if IVDBDEBUG:
            print("{ivdbase.Load()} loading - %s" % filename)
        try:
            with open(filename, 'r', encoding="utf-8") as f:
                for line in f:
                    # CSV line must be of the format: "sn, desc, wgt\n"
                    elements = ivdbase.lineDec(line)
                    if elements == None:
                        raise ValueError("File {%s} is badly formatted, expecting at least 3 values per line." % filename)
                    self.dblist.append( ivdbase.recGen( elements[0], elements[1], elements[2]) )
            self.dblen = len(self.dblist)
            if IVDBDEBUG:
                print("{ivdbase.Load()} %s records added" % self.dblen )
        except FileNotFoundError:
            print("Error, file not found.")
            return -1
        return self.dblen

    def Save(self, filename):
        if not filename.endswith('.csv'):
            filename += '.csv'
        with open(filename, 'w', encoding="utf-8") as f:
            idx = 0
            for r in self.dblist:
                f.write( ivdbase.lineGen(self.dblist[idx]) )
                idx += 1
        return idx

    # ver 1.0 - can only read one object
    def Read(self, idx):
        if idx < self.Size():
            return self.dblist[idx]
        else:
            return None

    def Append(self, dobj):
        self.dblist.append(dobj)
        self.dblen += 1
        return 0
    
    def Replace(self, index, dobj):
        try:
            self.dblist[index] = dobj
        except IndexError:
            if self.dblen > 0:
                print("{ivdbase.Replace()} Index (%s) out of Range, max allowable is (%s)" % (index, self.dblen-1))
            else:
                print("{ivdbase.Replace()} database is empty.")
            return -1
        return 0


if __name__ == '__main__':
    print("Testing ivdbase...")
    IVDBDEBUG = True
    db = ivdbase()

    # should not work...
    if db.Replace(0, ivdbase.recGen(1, "impossible", 88) ) < 0:
        print("Replace test: passed")
    else:
        print("Replace test: failed")

    # Try to load a bad record file
    if db.Load("./foo-bar.csv") < 0:
        print("Load test: passed")
    else:
        print("Load test: failed")

    # Add some Records
    print("Adding 10 records...")
    for i in range(1,11):
        print( "[%s] test-line-%s wgt:%s" % (i, i, 10*i) )
        db.Append( ivdbase.recGen(i, "test-line-%s"%i, 10*i) )
    
    # Try editing (Replacing)
    if db.Replace(1, ivdbase.recGen(2, "replaced-line-2", 99) ) == 0:
        print("Replace test: passed")
    else:
        print("Replace test: failed")
    if db.Replace(20, ivdbase.recGen(20, "impossible", 999) ) < 0:
        print("Replace test: passed")
    else:
        print("Replace test: failed")

    # Try getting the index of a serial number
    isn = 5
    rc = db.IndexOfSN(isn)
    print("Testing IndexOfSN(5), returned: %d" % rc)

    print("Dumping the internal database...")
    print(db.dblist)

    # Save it to file
    print("saving test.csv...")
    sc = db.Save("./test.csv")
    print("saved %s lines." % sc)

    # reset dbase and reac-back the file
    print("resetting database...")
    db.Reset()
    print("reading test file test.csv back into the database...")
    sc = db.Load("./test.csv")
    print("read %s lines back in." % sc)

    # report the records
    for i in range(sc):
        obj = db.Read(i)
        (sn, desc, wgt) = ivdbase.recDec(obj)
        print("[%s] sn = %s , desc = %s, weight = %s"% (i, sn, desc, wgt) )
    
    print("End test.")
