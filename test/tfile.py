import test.data as data
from os.path import exists
from test_util import test, only_if
from las.file import *
from las.headers import *
from las.parser import Parser
from las.util import subdivide, partial, times, float_eq

tests = []
test = partial(test, tests)
tf_path = "test/files/test.las"

#Test Attributes
@test
def header_get_attributes():
    ch = data.curve_header
    assert ch.depth.unit == "m"
    assert ch.porosity.unit == "m3/m3"
    assert ch.porosity.description == "Gamma"
    assert ch.netgross.description == "NetGross"
    assert ch.depth.description == "trend"

@test
def header_attributes():
    wh = data.well_header
    assert wh.strt.data == "1499.8790000"
    assert wh.strt.unit == "m"
    assert wh.comp.description == "COMPANY"        

@test
def descriptor_to_las():
    d = Descriptor("DEPT", "m", None, "DEPTH")
    parser = Parser(d.to_las())
    nd = parser.descriptor()
    assert d == nd
    
#Test Writing
@test
def data_to_las():
    ch = data.curve_header
    cols = len(ch.descriptors)
    parser = Parser(data.text['las_data'])
    curves = parser.las_data(ch)

    parser = Parser(LasCurve.to_las(curves))
    ncurves = parser.las_data(ch)
    assert curves == ncurves

@test
@only_if(exists(tf_path))
def lasfile_to_las():
    ol = LasFile.from_(tf_path)
    parser = Parser(ol.to_las())
    nl = parser.las_file()
    assert ol == nl
    
@test
@only_if(exists(tf_path))
def write_lasfile():
    lf =  LasFile.from_(tf_path)
    lf.depth[0] = "yack"
    assert "yack" in lf.to_las()    

#Test Transformed Las Field

@test
def test_lasfield():
    field = LasCurve(data.curve_header.descriptors[0], data.depths)
    for i in range(0, len(data.depths)):
        assert field[i] == data.depths[i]    

@test
def test_transformed_lasfield1():
    field = LasCurve(data.curve_header.descriptors[0], list(data.depths))
    scale = 3.3
    offset = 0 
    tfield = TransformedLasCurve(field, scale, offset)
    for i in range(0, len(data.depths)):
        assert tfield[i] == data.depths[i] * scale

@test
def test_transformed_lasfield2():
    field = LasCurve(data.curve_header.descriptors[0], list(data.depths))
    scale = 4.53
    offset = 0
    tfield = TransformedLasCurve(field, scale, offset)
    for i in range(0, len(data.depths)): 
        tfield[i] = tfield[i] + 1 * scale
    for i in range(0, len(data.depths)):
        assert float_eq(tfield[i] / scale, data.depths[i] + 1)

if __name__ == "__main__":
    for test in tests:
        test()
