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
COURTS = [
    "#place_MELBOURNE PETTY SESSIONS",
    "#place_CARLTON PETTY SESSIONS",
    "#place_NORTH MELBOURNE PETTY SESSIONS",
    "#place_COBURG PRISON POLICE MAGISTRATE",
    "#place_UNKNOWN",
    "#place_FITZROY PETTY SESSIONS",
    "#place_CALRTON PETTY SESSIONS",
    "#place_SOUTH MELBOURNE PETTY SESSIONS",
    "#place_RICHMOND PETTY SESSIONS"
]

COUNT_FORS = 3
COUNT_SEOS = 2
COUNT_INCLUDERS = 2

global conv_locations
global sentences

# Resolving linked items with multiple values

# can resolve multiple links two hops from an item
def test_resolve_sentences():
    pItem = crate.dereference(PERSONID)
    item = pItem.as_jsonld()
    global sentences
    sentences = crate.resolve(item, [{'property': 'conviction'}])
    assert len(sentences) == NCONVICTIONS


def test_resolve_multiple_properties():

    pItem = crate.dereference(PERSONID)
    item = pItem.as_jsonld()
    global conv_locations
    conv_locations = crate.resolve(item, [{'property': 'conviction'}, {'property': 'location'}])

    assert len(conv_locations) == len(COURTS)


def test_resolved_id_should_be_in_location():
    # all of the location ids from the convictions are in the location list
    error = False
    loc_ids = map(lambda l: l['@id'], conv_locations)
    list_locs_ids = list(loc_ids)
    for s in sentences:
        location_id = s['location']['@id'] or None
        if location_id not in list_locs_ids:
            error = True
    assert not error
