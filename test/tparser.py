from test.test_util import test, only_if
from las.file import *
from las.headers import *
from las.util import partial, forall, subdivide
from las.parser import BaseParser,Parser
import las.parser as lp
from test import data

tests = []
test = partial(test, tests)
enable_las_testing = True
las_test = only_if(enable_las_testing)

@test
def test_zapping():
    parser = BaseParser(data.text['well_header'])
    parser.drop_line()
    assert parser.zap_line() == "~Well"
    parser.goto_line("UWI")
    assert parser.zap_line() == "UWI.      : UNIQUE WELL ID"
    assert parser.upto(".") == "API"
    assert parser.upto(" ").strip() == ""
    parser.restart()
    parser.goto_line("DATE")
    assert parser.upto(".") == "DATE"
    assert parser.upto(" ").strip() == ""
    assert (parser.limit_line(lambda: parser.upto_last(":").strip())
           == "Monday, January 26 2009 14:04:02")

@test
@las_test
def test_descriptors():
    def parse(name):
        parser = Parser(data.text['descriptors'][name])
        ret = parser.descriptor()
        return ret

    dept = parse('dept')
    net_gross = parse('netgross')
    facies = parse('facies')
    porosity = parse('porosity')
    gamma = parse('gamma')
    depth = parse('depth')
    start = parse('strt')
    stop = parse('stop')
    date = parse('date')

    assert dept == Descriptor(mnemonic="DEPT",unit="m",description="DEPTH")
    assert net_gross == Descriptor(mnemonic="NetGross", description="NetGross")
    assert facies == Descriptor(mnemonic="Facies", description="Facies")
    assert porosity == Descriptor(mnemonic="Porosity", unit="m3/m3", description="Porosity")
    assert gamma == Descriptor(mnemonic="Gamma", unit="gAPI", description="Gamma")
    assert depth == Descriptor(mnemonic="DEPTH", unit="m", description="trend")
    assert start == Descriptor(mnemonic="STRT", unit="m", data=1499.8790000)
    assert stop == Descriptor(mnemonic="STOP", unit="m", data=2416.3790000)
    assert date == Descriptor(mnemonic="DATE",
                              data="Monday, January 26 2009 14:04:02",
                              description="DATE")
@test
@las_test
def test_version_header():
    parser = Parser(data.text['version_header'])
    version_header = parser.version_header()
    assert version_header == VersionHeader(2.0, False)
    
@test
@las_test
def test_well_header():
    parser = Parser(data.text['well_header'])
    well_header = parser.well_header()
    assert well_header.date.data == "Monday, January 26 2009 14:04:02"
    assert well_header.date.description == "DATE"

@test
@las_test
def test_curve_header():
    parser = Parser(data.text['curve_header'])
    curve_header = parser.curve_header()
    mnemonics = curve_header.mnemonics()
    assert len(curve_header.descriptors) == 6
    assert forall(["dept", "netgross", "facies", "porosity", "gamma", "depth"],
                  lambda m: m in mnemonics)

@test
@las_test
def test_las_data():
    parser = Parser(data.text['las_data'])
    cols = len(data.curve_header.descriptors)
    curves = parser.las_data(data.curve_header)
    assert len(curves) == cols
    for curve in curves:
        assert len(curve.to_list()) == 9

from os.path import exists

tf_path = "test/files/"

@test
@las_test
@only_if(exists(tf_path+"test.las"))
def test_las_file():
    lf = LasFile.from_(tf_path+"test.las")
    assert lf.dept[0] == 1501.6290000
    assert lf.curve_header.gamma.unit == 'gAPI'
    assert lf.curve_header.porosity.unit == 'm3/m3'
    assert lf.curve_header.dept.description == 'DEPTH'

@test
@las_test
@only_if(exists(tf_path+"dollie.las"))
def test_dollie():
    lf = LasFile.from_(tf_path+"dollie.las")
    assert lf.curve_header.dept.unit == "F"
    assert lf.dept[0] == 7800
    assert lf.dept[-1] == 6680
    assert lf.curve_header.wtoc.unit == "LBF/LBF"

@test
@las_test
@only_if(exists(tf_path+"x4.las"))
def test_x4():
    lf = LasFile.from_(tf_path+"x4.las")


if __name__ == "__main__":
    for test in tests:
        test()
