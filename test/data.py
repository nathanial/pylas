from las.file import *
from las.headers import *

curve_header = CurveHeader([
        Descriptor(mnemonic="DEPT", unit="m", description="DEPTH"),
        Descriptor(mnemonic="NetGross", description="NetGross"),
        Descriptor(mnemonic="Facies", description="Facies"),
        Descriptor(mnemonic="Porosity", unit="m3/m3", description="Gamma"),
        Descriptor(mnemonic="Gamma", unit="gAPI", description="Gamma"),
        Descriptor(mnemonic="DEPTH", unit="m", description="trend")])

well_header = WellHeader([
        Descriptor(mnemonic="STRT", unit="m", data="1499.8790000"),
        Descriptor(mnemonic="STOP", unit="m", data="2416.3790000"),
        Descriptor(mnemonic="COMP", description="COMPANY"),
        Descriptor(mnemonic="DATE", data="Monday, January 26 2009 14:04:02 : DATE")])

depths = [123.123, 124.124, 125.521, 99099.0, 
          99123, 8542, 123.02, 347.902, 111.2]

text = {}
text['well_header'] = """
~Well
STRT .m      1499.8790000 :
STOP .m      2416.3790000 :
STEP .m     0.00000000 :
NULL .        -999.250000 :
COMP.           : COMPANY
WELL.  A10   : WELL
FLD.            : FIELD
LOC.            : LOCATION
SRVC.           : SERVICE COMPANY
DATE.  Monday, January 26 2009 14:04:02   : DATE
PROV.           : PROVINCE
UWI.      : UNIQUE WELL ID
API.            : API NUMBER
"""
text['curve_header'] = """
~Curve
DEPT .m                   : DEPTH
NetGross .                : NetGross
Facies .                  : Facies
Porosity .m3/m3           : Porosity
Gamma .gAPI               : Gamma
DEPTH .m                  : trend
"""

text['descriptors'] = dict(
    dept="DEPT .m                   : DEPTH\n",
    netgross="NetGross .                : NetGross\n",
    facies="Facies .                  : Facies\n",
    porosity="Porosity .m3/m3           : Porosity\n",
    gamma="Gamma .gAPI               : Gamma\n",
    depth="DEPTH .m                  : trend\n",
    strt="STRT .m      1499.8790000 :",
    stop="STOP .m      2416.3790000 :",
    step="STEP .m     0.00000000 :",
    null="NULL .        -999.250000 :",
    comp="COMP.           : COMPANY",
    well="WELL.  A10   : WELL",
    fld="FLD.            : FIELD",
    loc="LOC.            : LOCATION",
    srvc="SRVC.           : SERVICE COMPANY",
    date="DATE.  Monday, January 26 2009 14:04:02   : DATE",
    prov="PROV.           : PROVINCE",
    uwi="UWI.      : UNIQUE WELL ID",
    api="API.            : API NUMBER",
    )

text['version_header'] = """
~Version information
VERS.   2.0:
WRAP.   NO:
"""

text['las_data'] = """
~Ascii
 1499.8790000 0.0000000000  -999.250000  -999.250000  -999.250000 1499.8790283
 1500.1290000 0.0000000000  -999.250000  -999.250000  -999.250000 1500.1290283
 1500.6290000 0.0000000000  -999.250000  -999.250000  -999.250000 1500.6290283
 1501.1290000 0.0000000000 0.0000000000 0.2706460059  -999.250000 1501.1290283
 1501.6290000 0.0000000000 0.0000000000 0.2674280107 78.869453430 1501.6290283
 1502.1290000 0.0000000000 0.0000000000 0.2560760081 78.008300781 1502.1290283
 1502.6290000 0.0000000000 0.0000000000 0.2421260029 75.581558228 1502.6290283
 1503.1290000 0.0000000000 0.0000000000 0.2385890037 73.238037109 1503.1290283
 1503.6290000 0.0000000000 0.0000000000 0.2383770049 71.504173279 1503.6290283
"""
