import re
import new
from util import lfind, tuplize, read_file

def preprocess_str(obj):
    if isinstance(obj, str):
        obj = obj.strip()
        if obj == "":
            return None
        else:
            return obj
    else:
        return obj

class LasFile(object):
    def __init__(self, version_header, well_header, curve_header, parameter_header, curves):
        self.version_header = version_header
        self.well_header = well_header
        self.curve_header = curve_header
        self.parameter_header = parameter_header
        self.curves = curves

        for mnemonic in self.curve_header.mnemonics():
            field = LasCurve.find_with_mnemonic(mnemonic, self.curves)
            setattr(self, mnemonic, field)

    def __eq__(self,that):
        return (isinstance(that, LasFile) and
                self.version_header == that.version_header and
                self.well_header == that.well_header and
                self.curve_header == that.curve_header and
                self.parameter_header == that.parameter_header and
                self.curves == that.curves)

    @staticmethod
    def from_(path):
        from las.parser import Parser
        return Parser(read_file(path)).las_file()

    @staticmethod
    def is_lasfile(filename):
        return True #fixme

    def to_las(self):
        return (self.version_header.to_las() +
                self.well_header.to_las() + 
                self.curve_header.to_las() +
                self.parameter_header.to_las() +
                LasCurve.to_las(self.curves))

    def curve_mnemonics(self):
        return self.curve_header.mnemonics()

    def get_curve(self, curve_name):
        return getattr(self, curve_name)

    def get_curves(self, *curve_names):
        return [self.get_curve(name) for name in curve_names]

    def available_curves(self):
        return self.curve_header.mnemonics()

class Descriptor(object):
    def __init__(self, mnemonic, unit = None, data = None, description = None):
        self.mnemonic = preprocess_str(mnemonic)
        self.unit = preprocess_str(unit)
        self.data = preprocess_str(data)
        self.description = preprocess_str(description)

    def __str__(self):
        return "mnemonic = %s, unit = %s, data = %s, description = %s" % (
            self.mnemonic, self.unit, self.data, self.description)

    def __repr__(self): return self.__str__()

    def __eq__(self, that):
        if not isinstance(that, Descriptor): return False
        return (self.mnemonic == that.mnemonic and
                self.unit == that.unit and
                self.data == that.data and
                self.description == that.description)

    def to_las(self):
        data, unit, description = " ", " ", " "
        if self.data != None: data = self.data
        if self.unit != None: unit = self.unit
        if self.description != None: description = self.description
        return (self.mnemonic+"."+unit+" "+str(data)+" : "+description)

class HasDescriptors(object):
    def mnemonics(self):
        return map(lambda d: d.mnemonic.lower(), self.descriptors)

class LasCurve(object):
    def __init__(self, descriptor, data):
        self.descriptor = descriptor
        self.data = data

    def __getitem__(self, idx):
        return self.get_at(idx)

    def __setitem__(self, idx, val):
        return self.set_at(idx, val)

    def set_at(self, idx, val):
        self.data[idx] = val

    def get_at(self, idx):
        return self.data[idx]

    def data_len(self):
        return len(self.data)

    def __eq__(self, that):
        if not isinstance(that, LasCurve): return False
        if not self.descriptor == that.descriptor: return False
        return not lfind(tuplize(self.data, that.data), 
                         lambda dd: dd[0] - dd[1] > 0.1)
        
    def __str__(self):
        return str(self.descriptor)
    
    def __repr__(self): return self.__str__()

    def to_list(self):
        return list(self.data)

    def name(self):
        return self.descriptor.mnemonic.lower()

    @staticmethod
    def from_rows(data_rows, curve_header):
        ds = curve_header.descriptors
        cols = len(ds)
        return [LasCurve(ds[i],map(lambda r: r[i], data_rows))
                for i in range(0, cols)]

    @staticmethod
    def to_las(curves):
        rows = len(curves[0].data)
        matrix = [[curve[row] for curve in curves] for row in range(0, rows)]
        lines = [" ".join(map(str,row)) for row in matrix]
        return "~Ascii\n" + "\n".join(lines)


    @staticmethod
    def find_with_mnemonic(mnemonic, curves):
        return lfind(curves, lambda f: f.descriptor.mnemonic.lower() == mnemonic)

class TransformedLasCurve(LasCurve):
    def __init__(self, lasfield, scale, offset):
        self.lasfield = lasfield
        self.scale = scale
        self.offset = offset
        LasCurve.__init__(self, lasfield.descriptor, lasfield.data)

    def set_at(self, idx, val):
        self.data[idx] = (val - self.offset) / (self.scale * 1.0) 
    
    def get_at(self, idx):
        return self.data[idx] * self.scale + self.offset

    def to_list(self):
        return [x * self.scale + self.offset for x in self.data]

def transform(field, scale, offset):
    return TransformedLasCurve(field, scale, offset)

