import re
import urllib.request


# TODO: this is needed because of a following standard rocrate
def remove_hash(string):
    line = re.sub('^[#]', '', string)
    return line


# TODO: this is needed because of a bug in standard rocrate
def prepend_hash(string):
    match = re.findall(r'^(#|arcp://)?', string)
    if not match:
        return '#' + string
    else:
        return string


def download_file(url, location, file_name):
    print(f'downloading : {url}')
    urllib.request.urlretrieve(url, location + file_name)
