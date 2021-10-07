from rocrate.rocrate import ROCrate
from rocrate_lang.transcription import Transcription
from os import path

abs_path = path.abspath(path.dirname(__file__))
transcriptions = []
crate_id = 'rocrate_test_f2f'

crate_base = path.join(abs_path, 'test-data')
crate_path = path.join(crate_base, crate_id)
crate = ROCrate(crate_path)
repo_url = 'file://' + crate_base


# Just test to see if rocrate is loaded
def test_load():
    assert crate.name == 'Farms to Freeways Example Dataset'


def test_transcript():
    global transcriptions
    t = Transcription(crate, repo_url, crate_id)
    transcriptions = t.load('OrthographicTranscription')
    assert len(transcriptions) > 0


def test_schema():
    t_list = list(transcriptions)
    t = (t_list[0])
    columns = t['schema']['columns']
    assert {'@id': '#time'} in columns
