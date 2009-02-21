import re
import new
from util import lfind, tuplize, read_file

class LasFile(object):
    def __init__(self, version_header, well_header, curve_header, parameter_header, curves):
        self.version_header = version_header
        self.well_header = well_header
        self.curve_header = curve_header
        self.parameter_header = parameter_header
        self._curves = curves
        self.path = None
        self._name = None
        self._index = None

    def __eq__(self,that):
        return (isinstance(that, LasFile) and
                self.version_header == that.version_header and
                self.well_header == that.well_header and
                self.curve_header == that.curve_header and
                self.parameter_header == that.parameter_header and
                self._curves == that._curves)

    def to_las(self):
        return (self.version_header.to_las() +
                self.well_header.to_las() + 
                self.curve_header.to_las() +
                self.parameter_header.to_las() +
                LasCurve.to_las(self._curves))

    def curve(self, curve_name):
        return lfind(self._curves, lambda c: c.name() == curve_name)

    def curves(self, *curve_names):
        return [self.curve(name) for name in curve_names]

    def curve_mnemonics(self):
        return self.curve_header.mnemonics()

    def available_curves(self):
        return self.curve_mnemonics()

    def has_curve(self, curve_name):
        return curve_name in self.available_curves()

    def name(self):
        if self._name: return self._name
        if self.path:
            m = re.match("(.*)/([^/]+)", str(self.path))
            return m.group(2)

    def index(self):
        if self._index:
            return self._index
        elif self.has_curve("dept"):
            return self.curve("dept")
        elif self.has_curve("depth"):
            return self.curve("depth")
        else:
            raise "Cannot find depth curve!"

    def set_index(self, name):    
        if self.has_curve(name):
            self._index = self.curve(name)
        else:
            raise "Cannot find curve %s " % name

    def index_name(self):
        return self.index().name()

    @staticmethod
    def from_(path):
        from las.parser import Parser
        lf = Parser(read_file(path)).las_file()
        lf.path = path
        return lf

    @staticmethod
    def is_lasfile(filename):
        return True #fixme

    def merge_left(self, *args, **kwargs):
        kind = kwargs.get('kind', 'at_end')
        that, = args
        if kind is 'at_end':
            new_curves = []
            for curve_name in self.available_curves():
                this_curve = self.curve(curve_name)
                that_curve = that.curve(curve_name)
                new_curve = this_curve.merge_left(that_curve, kind='at_end')
                new_curves.append(new_curve)
            return LasFile(self.version_header,
                           self.well_header,
                           self.curve_header,
                           self.parameter_header,
                           new_curves)

    def merge_right(self, *args, **kwargs):
        that = args[0]
        args = args[1:]
        return that.merge_left(self,*args, **kwargs)
            
            
class Descriptor(object):
    def __init__(self, mnemonic, unit = None, data = None, description = None):
        self.mnemonic = mnemonic
        self.unit = unit
        self.data = data
        self.description = description

    def __str__(self):
        return "mnemonic = %s, unit = %s, data = %s, description = %s" % (
            self.mnemonic, self.unit, self.data, self.description)

    def __repr__(self): return self.__str__()

    def __eq__(self, that):
        if isinstance(that, Descriptor):
            return (self.mnemonic == that.mnemonic and
                    self.unit == that.unit and
                    self.data == that.data and
                    self.description == that.description)
        elif isinstance(that, float) or isinstance(that, int):
            return self.data == that
        else:
            return NotImplemented

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
        if not isinstance(that, LasCurve): 
            return False
        if not self.descriptor == that.descriptor: 
            return False
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

    def merge_left(self, *args, **kwargs):
        kind = kwargs.get('kind', 'at_end')
        that, = args
        if not that.descriptor == self.descriptor:
            raise "illegal merge of distinct curves %s %s" % (self, that)
        if kind is 'at_end':
            slen = len(self.data)
            tlen = len(that.data)
            new_data = list(self.data)
            for i in range(slen, tlen):
                new_data.append(that.data[i])
            return LasCurve(self.descriptor, new_data)
        else:
            raise "merge kind not recognized"

    def merge_right(self, *args, **kwargs):
        that = args[0]
        args = args[1:]
        return that.merge_left(self, *args, **kwargs)
    
    def min(self):
        return min(self.to_list())
    
    def max(self):
        return max(self.to_list())
    
        
    
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

