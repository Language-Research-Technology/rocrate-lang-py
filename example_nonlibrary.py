import json
import itertools
import pandas as pd

BASE_URL = 'file://'

# Farms To Freeways
F2F_CRATE_PATH = 'test/test-data/'
F2F_DATASET_ID = 'farms_to_freeways_test_rocrate/'

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
                    all_data[t] = pd.concat([all_data[t], df])

new = pd.merge(left=all_data['TextDialogue'], right=all_data[hypernym['speaker']], left_on='speaker.@id', right_on='@id',
               suffixes=('_artefact', '_speaker'), how='inner')
print(new.loc[0]['@type_artefact'])
print(new.loc[0]['@type_speaker'])
print(new.loc[0])

print(new.keys())


# Statistical Summaries

# In the metadata there is a key called "birthDate" which is a string that only
# has the birth year of the speaker. One of the birthDate values in the metadata
# has a string value "c 1924", instead of a simply sequence of digits there is,
# as shown when the list of birthDates are printed
print(new.birthDate)

# The value for birthDate is a list, which is indicated by the []. We can flatten
# this list by iterating over each of these lists:
print([y for y in list(itertools.chain.from_iterable(new.birthDate))])

# The value "c 1924" needs to be normalised as a regular looking year, ie 4 numbers in a sequence.
# This can be done by simply only allowing the last 4 characters in any string that is a birthDate.
# For example if year0 = "1918" and year1 = "c 1924" and we only take the last 4 characters, then
# year0[-4:] = "1918" and year1[-4:] = "1924".

# 'birthDate' only has the year listed as a text string (str), therefore we need to convert
# the birthDate value from str to an integer (int) if we want to do any statistical operations
# based on birthDate. This conversion can be done by 'type casting', eg, if year is a string
# that has the value "1924", we simply impose the type int(), such as int(year),
# so the string year = "1924" => integer, year = 1924, which is then a number (not a string)
# that can undergo maths operations.

# The function int(...) in the following line imposes an integer type conversion. That is, int(x)
# converts x from whatever type it is into an integer, as long as it makes sense for x to be converted
# into an integer. For example if x = "abc", then it would be impossible to know what value x would
# have as an integer. But if a string x = "1924", then the integer would have the value 1924.

# birth_year = [int(y[-4:]) for sublist in new.birthDate for y in sublist]
birth_year = [int(y[-4:]) for y in list(itertools.chain.from_iterable(new.birthDate))]

# We can calculate the mean (average) age
this_year = datetime.datetime.now().year
# Create a list called 'age' which takes every year in birth_year as y. Then get this_year and minus that
# number from year y and make sure all those numbers are stored in a list, which is why we have [] around the
# whole sequence of instructions below.
age = [this_year - y for y in birth_year]

# Print the list of the age of all the speakers if they were all alive today
print(age)

# Print the mean age, which is the average age of all the speakers
print(statistics.mean(age))
# The mode is the most freqently occur age. That is, there are more speakers of this age than any other.
print(statistics.mode(age))
# The median is the middle value if the age of the participants were listed in order.
print(statistics.median(age))
# The standard deviation is a statistical metric that gives us an indication of how dispersed the age range of the speakers is
print("{:.1f}".format(statistics.stdev(age)))

# Print the mean, median, mode and standard deviation of the birth year
print(statistics.mean(birth_year))
print(statistics.median(birth_year))
print(statistics.mode(birth_year))
print("{:.1f}".format(statistics.stdev(birth_year)))

# Other Metadata Features: Place

place_of_story = list(itertools.chain.from_iterable(new.address))
place_of_birth = list(itertools.chain.from_iterable(new.birthPlace))

# How many of the interviews talked about a certain location/city/suburb
count_story_place = dict(Counter(place_of_story))
pprint.pp(count_story_place, sort_dicts=True)

# There is a location 'Penrith' as well as 'Kingston, Penrith'
# There is a location 'St. Marys' as well as 'St Marys' (no '.')
# Let's normalise these locations
place_of_story = [p.split(',')[-1].replace('.', '').strip() for p in place_of_story]
count_story_place = dict(Counter(place_of_story))
pprint.pp(count_story_place, sort_dicts=True)

# Count place of birth
place_of_birth = [p.split(',')[-1].replace('.', '').strip() for p in place_of_birth]
count_birth_place = dict(Counter(place_of_birth))
pprint.pp(count_birth_place, sort_dicts=True)

# Cross-cutting 2 features found in the metadata

# Print place of story and story teller's birth year
print(new.columns)
print(len(new))
print(new['address'])

new['address'] = new['address'].apply(lambda x: x[0].split(',')[-1].replace('.', '').strip())

a = new.loc[new['address'] == 'Blacktown']
print(a.birthDate)

for town in set(place_of_story):
    subset = new.loc[new['address'] == town]
    year = [int(y[-4:]) for y in itertools.chain.from_iterable(subset['birthDate'])]
    print(town, sorted(year))

    my_row = list()

    for row in range(len(subset)):
        my_row.append((subset.iloc[row]['birthDate'][0], subset.iloc[row]['name_speaker'][0]))
    print(town, my_row)


