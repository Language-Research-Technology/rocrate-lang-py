import re
import urllib.request
import collections


# TODO: this is needed because of a following standard rocrate
def remove_hash(string):
    line = re.sub('^[#]', '', string)
    return line


def download_file(url, location, file_name):
    print(f'downloading : {url}')
    urllib.request.urlretrieve(url, location + file_name)

# Copied verbatim from ro-crate#1.1
# https://github.com/ResearchObject/ro-crate-py/tree/ro-crate-1.1
def as_list(list_or_other):
    if list_or_other is None:
        return []
    if (isinstance(list_or_other, collections.abc.Sequence)
        and not isinstance(list_or_other, str)): # FIXME: bytes?
        return list_or_other
    return [list_or_other]
