import json
import itertools
import pandas as pd

BASE_URL = 'file://'

# Farms To Freeways
F2F_CRATE_PATH = '/PATH/TO/ROCRATE/'
F2F_DATASET_ID = 'farms_to_freeways/'

# KEYWORDS from RO-CRATE
OBJECT_LINKAGE = 'hasFile'
GRAPH = '@graph'
TYPE = '@type'
ID = '@id'
PRIMARY_OBJECT = 'RepositoryObject'

json_filename = 'ro-crate-metadata.json'
crate_file = F2F_CRATE_PATH+F2F_DATASET_ID+json_filename
metadata = json.load(open(crate_file, 'r'))

# Find all types and find types that have linked objects
linked_objects = set()
types = list()
primary_object_types = set()
for entity in metadata[GRAPH]:
    my_type = entity[TYPE]
    if type(my_type) == str:
        my_type = [my_type]
    if my_type not in types:
        types.append(my_type)

    # [PRIMARY_OBJECT, X] : primary_object_type = X
    if PRIMARY_OBJECT in my_type:
        primary_object_type = [e for e in my_type if e not in [PRIMARY_OBJECT]][0]
        primary_object_types.add(primary_object_type)

    if OBJECT_LINKAGE in entity:
        for x in entity[OBJECT_LINKAGE]:
            filename = x[ID]
            suffix = filename.split('.')[-1]
            if suffix not in linked_objects:
                linked_objects.add((suffix, primary_object_type))


flat_types = list(itertools.chain.from_iterable(types))

# All the types
print(sorted(types))

# All the unique types
print(set(flat_types))

# Types of PRIMARY_OBJECTs ie [PRIMARY_OBJECT, X]. What kinds of Xs do we have?
print(primary_object_types)

# All the entity types that are referred to with an OBJECT_LINKAGE
print(linked_objects)

# The problem with this ro-crate is that you need knowledge like 'speaker' is a kind of 'Person'
# in order to link an artefact (ie dialogue transcript) with the speaker being interviewed
hypernym = dict()
hypernym['speaker'] = 'Person'

# We think that the primary object types are the ones we may care about
# so we will pull them into their own dataframe
# all_data = dict.fromkeys(primary_object_types, pd.DataFrame())
# print(all_data.keys())
all_data = dict()
for entity in metadata[GRAPH]:
    if type(entity[TYPE]) == list:
        for t in entity[TYPE]:
            if t in primary_object_types:
                df = pd.json_normalize(entity)
                if t not in all_data:
                    all_data[t] = df
                else:
                    all_data[t].append(df)

for e in all_data:
    ...
    # print(e)
    # print(all_data[e].keys())

new = pd.merge(left=all_data['TextDialogue'], right=all_data[hypernym['speaker']], left_on='speaker.@id', right_on='@id', how='inner')
print(new.loc[0])

