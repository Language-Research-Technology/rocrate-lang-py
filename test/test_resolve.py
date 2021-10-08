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


# Conditional resolution with include

crate2_id = 'resolve_crate_include'

crate2_base = path.join(abs_path, 'test-data')
crate2_path = path.join(crate2_base, crate2_id)
crate2 = ROCratePlus(crate2_path)

global includers


# can resolve items of a particular type, via include
def test_resolve_type_via_include():
    root = crate2.root_dataset
    global includers
    includers = crate2.resolve(root.as_jsonld(), [{
        'property': 'hasPart',
        'includes': {'@type': 'ImageObject'}
    }])
    assert len(includers) == COUNT_INCLUDERS


def test_verify_includers():
    error = False
    for i in list(includers):
        if not i['@type'] == 'ImageObject':
            error = True
    assert not error


# Conditional resolution with matchFn
# can resolve items which match a regexp
def test_resolve_with_matchFn():
    root = crate2.root_dataset
    for_codes = crate2.resolve(root.as_jsonld(), [{
        'property': 'about',
        'matchFn': lambda item: re.search(r"anzsrc-for", item["@id"])
    }])
    assert len(for_codes) == COUNT_FORS


def test_resolve_with_matchFn_2():
    root = crate2.root_dataset
    seo_codes = crate2.resolve(root.as_jsonld(), [{
        'property': 'about',
        'matchFn': lambda item: re.search(r"anzsrc-seo", item["@id"])
    }])
    assert len(seo_codes) == COUNT_SEOS


# Collect items when resolving links
global crate_finals
global subgraph


# int generates a subgraph of all items traversed when resolving
def test_subgraph():
    pItem = crate.dereference(PERSONID)
    item = pItem.as_jsonld()
    global crate_finals
    global subgraph
    [crate_finals, subgraph] = crate.resolveAll(item, [{'property': "conviction"}, {'property': "location"}]);

    assert any(crate_finals and subgraph)


# the subgraph should contain all of the convictions it traversed,
# and all of the locations, and nothing else
def test_subgraph_contains_convictions_and_locations():
    pItem = crate.dereference(PERSONID)
    item = pItem.as_jsonld()
    convictions = crate.resolve(item, [{'property': "conviction"}])
    courts = crate.resolve(item, [{'property': "conviction"}, {'property': "location"}])

    c_ids = map(lambda l: l['@id'], convictions)
    list_c_ids = list(c_ids)
    cl_ids = map(lambda l: l['@id'], courts)
    list_cl_ids = list(cl_ids)

    sg_ids = map(lambda l: l['@id'], subgraph)
    list_sg_ids = list(sg_ids)

    expect_ids = list_c_ids + list_cl_ids

    assert expect_ids == list_sg_ids