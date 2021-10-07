from .utils import *


class Transcription:
    def __init__(self, crate, repo_url, dataset_id):
        self.crate = crate
        self.repo_url = repo_url
        self.dataset_id = dataset_id
        self.orto = []

    def load(self, crate_type):
        for e in self.crate.get_entities():
            if crate_type in e.type:
                print(e.as_jsonld())
                json = e.as_jsonld()
                json['@id'] = remove_hash(json['@id'])
                json['@id'] = self.repo_url + self.dataset_id + json['@id']
                if 'csvw:tableSchema' in json:
                    schemas = json['csvw:tableSchema']
                    del json['csvw:tableSchema']
                    type_schema = type(schemas).__name__
                    if type_schema == 'dict':
                        schema = self.crate.dereference(schemas['@id'])
                        json['schema'] = schema.as_jsonld()
                        json['schema']['@id'] = remove_hash(json['schema']['@id'])
                        json['schema']['@id'] = self.repo_url + self.dataset_id + json['schema']['@id']
                self.orto.append(json)
        # Do something with the Orthographic Transcription
        return self.orto
