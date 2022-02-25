from rocrate_lang.rocrate_plus import ROCratePlus
from os import path
import re
import pandas as pd

abs_path = path.abspath(path.dirname(__file__))
crate_base = path.join(abs_path, 'test-data')


# it can resolve multiple reverse links
def test_resolve_reverse_conviction():
    PERSONID = '#person___VICFP_18551934_14_8'
    NCONVICTIONS = 58
    crate_id = 'resolve_crate'
    crate_path = path.join(crate_base, crate_id)
    crate = ROCratePlus(crate_path)
    pItem = crate.dereference(PERSONID)
    item = pItem.as_jsonld()
    crate.addBackLinks()
    global convictions
    global convictions_r

    convictions_r = crate.resolve(item, [{'property': "object", "@reverse": True}])
    convictions = crate.resolve(item, [{'property': "conviction"}])

    assert (len(convictions_r) == NCONVICTIONS) and (len(convictions_r) == len(convictions))


crate_f2f_id = 'farms_to_freeways_test_rocrate'
crate_f2f_path = path.join(crate_base, crate_f2f_id)
crate_f2f = ROCratePlus(crate_f2f_path)
crate_f2f.addBackLinks()

global interviews


# it can resolve multiple reverse links
def test_resolve_reverse_farms():
    interviews_item = crate_f2f.dereference('#interviews')
    interviews_item_json = interviews_item.as_jsonld()
    global interviews
    interviews = []
    for member in interviews_item_json['hasMember']:
        interview = crate_f2f.dereference(member['@id'])
        interview_json = interview.as_jsonld()
        speaker = crate_f2f.resolve(interview_json, [
            {'property': "speaker"}
        ])
        if speaker:
            interview_json['speaker'] = speaker
        files = crate_f2f.resolve(interview_json, [
            {'property': "hasFile"}
        ])

        if files:
            interview_json['files'] = files
            del interview_json['hasFile']

        interviews.append(interview_json)

    assert len(interviews) == 34
