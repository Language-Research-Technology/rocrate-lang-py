import re
import urllib.request


# TODO: this is needed because of a following standard rocrate
def remove_hash(string):
    line = re.sub('^[#]', '', string)
    return line


def download_file(url, location, file_name):
    print(f'downloading : {url}')
    urllib.request.urlretrieve(url, location + file_name)
