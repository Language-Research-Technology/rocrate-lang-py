# Using rocrate#fix_data_entity pip install git+https://github.com/ResearchObject/ro-crate-py.git#fix_data_entity
from rocrate.rocrate import ROCrate
import re
import urllib.request


def main():
    BASE_URL = 'file://'
    CRATE_PATH = '/Users/moises/cloudstor/Shared/atap-repo-misc/'
    REPO_DATASET_ID = 'farms_to_freeways/'

    print(f'Loading:  {CRATE_PATH + REPO_DATASET_ID}')
    repo_url = BASE_URL + CRATE_PATH
    crate = ROCrate(CRATE_PATH + REPO_DATASET_ID)
    orto = []
    for e in crate.get_entities():
        if 'OrthographicTranscription' in e.type:
            print(e.as_jsonld())
            json = e.as_jsonld()
            json['@id'] = remove_hash(json['@id'])
            json['@id'] = repo_url + REPO_DATASET_ID + json['@id']
            if 'csvw:tableSchema' in json:
                schemas = json['csvw:tableSchema']
                del json['csvw:tableSchema']
                typeSchema = type(schemas).__name__
                if typeSchema == 'dict':
                    schema = crate.dereference(schemas['@id'])
                    json['schema'] = schema.as_jsonld()
                    json['schema']['@id'] = remove_hash(json['schema']['@id'])
                    json['schema']['@id'] = repo_url + REPO_DATASET_ID + json['schema']['@id']
            orto.append(json)
    # Do something with the Orthographic Transcription
    orto

    for o in orto:
        download_file(o['@id'], 'test/test-data/', o['name'] + '.csv')


# TODO: this is needed because of a bug in rocrate-py library
def remove_hash(string):
    line = re.sub('^[#]', '', string)
    return line


def download_file(url, location, file_name):
    print(f'downloading : {url}')
    urllib.request.urlretrieve(url, location + file_name)


if __name__ == '__main__':
    main()
