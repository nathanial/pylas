import re
from las.file import *
from las.headers import *
from util import subdivide
import test.data as data

num_regex = "-?\d+([.]\d+)?"
start_symbols = ["~A", "~C", "~W", "~P", "~V"]

def is_number(text):
    match = re.match(num_regex, text)
    if match:
        start = match.start()
        end = match.end()
        return (end - start) == len(text)
    else:
        return False

def to_num(text):
    try:
        return int(text)
    except ValueError:
        return float(text)

class Parser:

    def __init__(self, input):
        self.input = input
        self.cursor = 0

    def las_file(self):
        version_header = self.version_header()
        well_header = self.well_header()
        curve_header = self.curve_header()
        parameter_header = self.parameter_header()
        las_data = self.las_data(curve_header)
        return LasFile(version_header,
                       well_header,
                       curve_header,
                       parameter_header,
                       las_data)
        

    def well_header(self): 
        parser = self.grab("~W")
        parser.well_start()
        descriptors = parser.descriptors()
        ret = WellHeader(descriptors)
        return ret
        
    def well_start(self):
        self.skip_spaces()
        self.linep().get("~W.*")

    def version_header(self):
        parser = self.grab("~V")
        parser.skip_spaces()
        assert parser.linep().get("~V.*")
        version = parser.linep().skip("VERS[.]").upto(":").strip()        
        version = to_num(version)        

        wrap = parser.linep().skip("WRAP[.]").upto(":").strip()
        if wrap == "NO": 
            wrap = False
        elif wrap == "YES":
            wrap = True
        else:
            raise "WRAP NOT RECOGNIZED"

        return VersionHeader(version, wrap)

    def curve_header(self):
        parser = self.grab("~C")
        parser.skip_spaces()
        assert parser.linep().get("~C.*")
        descriptors = parser.descriptors()
        return CurveHeader(descriptors)

    def parameter_header(self):
        parser = self.grab("~P")
        parser.skip_spaces()
        assert parser.linep().get("~P.*")
        descriptors = parser.descriptors()
        return ParameterHeader(descriptors)

    def las_data(self, curve_header):
        parser = self.grab("~A")
        parser.skip_spaces()
        assert parser.linep().get("~A.*")
        data = []
        for line in self.lines():
            numbers = Parser(line).get_numbers()
            data = data + numbers
        return LasCurve.from_rows(subdivide(data, len(curve_header.descriptors)),
                                  curve_header)

    def get_numbers(self):
        num = self.get_ignore_space(num_regex)
        nums = []
        while num:
            nums.append(to_num(num))
            num = self.get_ignore_space(num_regex)
        return nums
    

    def descriptors(self):
        descriptor = self.descriptor()
        acc = []
        while descriptor: 
            acc.append(descriptor)
            descriptor = self.descriptor()
        return acc

    def descriptor(self):
        self.skip_spaces()
        line = self.line()
        if line:
            if line.strip()[:2] in start_symbols: 
                self.backtrack(line)
                return
            parser = Parser(line)
            mnemonic = parser.upto("[.]")
            unit = parser.zapto("[ ]")
            data = parser.zapto_last("[:]")
            if data: 
                data = data[:-1].strip()
                if is_number(data): 
                    data = to_num(data)
                
            description = parser.current_input()
            return Descriptor(mnemonic, unit, data, description)
        
    def skip_spaces(self):
        match = re.match("\A[\n\r\t ]+", self.current_input())
        if match: self.cursor += match.end()

    def backtrack(self, text):
        self.cursor -= len(text)

    def line(self):
        ret = self.zapto("\n")
        if not ret:
            ret = self.current_input()
            self.cursor = len(self.input)
        elif ret.strip() != "" and ret.strip()[0] == "#":
            ret = self.line()
        return ret
        
        
    def lines(self):
        l = self.line()
        while l:
            yield l
            l = self.line()

    def linep(self):
        return Parser(self.line())

    def rest(self):
        return self.current_input()

    def current_input(self):
        return self.input[self.cursor:]

    def zapto_last(self, pattern):
        return self.do_match("\A.*"+pattern, 0)

    def zapto(self,pattern):
        return self.do_match("(\A.*?)"+pattern, 0)

    def upto(self,pattern):
        ret = self.do_match("(\A.*?)"+pattern, 0)
        if ret: return ret[:-1]
        

    def get_ignore_space(self, pattern):
        return self.do_match("(\A[\n\r\t ]*)("+pattern+")", 2)

    def get(self, pattern):
        return self.do_match("\A"+pattern, 0)

    def grab(self, pattern):
        cinput= self.current_input()
        match = re.search(pattern, cinput)
        if match:
            start = match.start()
            return Parser(cinput[start:])
            
            

    def skip(self, pattern):
        self.skip_spaces()
        self.get(pattern)
        return self

    def do_match(self, pattern, group):
        cinput = self.current_input()
        match = re.match(pattern, cinput)
        if match:
            start = match.start()
            end = match.end()
            ret = cinput[start:end]
            self.cursor += match.end()
            return ret
            

            
    

if __name__ == "__main__":
#    parser = Parser(text)
#    print Parser.zapto(text, "c")
#    print Parser.pull(text, "\n")
#    parser = Parser(data.text['well_header'])
#    for line in parser.lines(): print "(%s)" % line

#    parser = Parser(data.text['well_header'])
#    print parser.well_start()

#    descriptors = data.text['descriptors']
#
#    parser = Parser(descriptors['dept'])
#    print parser.descriptor()
#
#    parser = Parser(descriptors['date'])
#    print parser.descriptor()

    print data.text['well_header']
    parser = Parser(data.text['well_header'])
    print parser.well_header()

    
