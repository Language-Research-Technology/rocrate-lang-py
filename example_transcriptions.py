from rocrate.rocrate import ROCrate
from rocrate_lang.transcription import Transcription
from rocrate_lang import utils


def main():
    BASE_URL = 'file://'
    CRATE_PATH = '/Users/moises/cloudstor/Shared/atap-repo-misc'
    REPO_DATASET_ID = 'farms_to_freeways'

    print(f'Loading:  {CRATE_PATH + REPO_DATASET_ID}')
    repo_url = BASE_URL + CRATE_PATH
    crate = ROCrate(CRATE_PATH + REPO_DATASET_ID)
    transcription = Transcription(crate, repo_url, REPO_DATASET_ID)
    orto = transcription.load('OrthographicTranscription')

    for o in orto:
        file_name = o['name'].replace(' ', '_')
        utils.download_file(o['@id'], 'test/test-data/', file_name + '.csv')


if __name__ == '__main__':
    main()
