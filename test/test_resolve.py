from rocrate_lang.rocrate_plus import ROCratePlus
from os import path

abs_path = path.abspath(path.dirname(__file__))
transcriptions = []
crate_id = 'resolve_crate'

crate_base = path.join(abs_path, 'test-data')
crate_path = path.join(crate_base, crate_id)
crate = ROCratePlus(crate_path)

PERSONID = '#person___VICFP_18551934_14_8'
NCONVICTIONS = 58


# Resolving linked items with multiple values

##can resolve multiple links two hops from an item
def test_multiple_links():
    pItem = crate.dereference(PERSONID)
    item = pItem.as_jsonld()
    sentences = crate.resolve(item, [{'property': "conviction"}])
    assert len(sentences) == NCONVICTIONS
