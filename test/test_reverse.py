from rocrate_lang.rocrate_plus import ROCratePlus
from os import path
import re

abs_path = path.abspath(path.dirname(__file__))
transcriptions = []
crate_id = 'resolve_crate'

crate_base = path.join(abs_path, 'test-data')
crate_path = path.join(crate_base, crate_id)
crate = ROCratePlus(crate_path)

PERSONID = '#person___VICFP_18551934_14_8'
NCONVICTIONS = 58

global convictions
global convictions_r


# it can resolve multiple reverse links
def test_resolve_reverses():
    pItem = crate.dereference(PERSONID)
    item = pItem.as_jsonld()
    crate.addBackLinks()
    global convictions
    global convictions_r

    convictions_r = crate.resolve(item, [{'property': "object", "@reverse": True}])
    convictions = crate.resolve(item, [{'property': "conviction"}])

    assert (len(convictions_r) == NCONVICTIONS) and (len(convictions_r) == len(convictions))
