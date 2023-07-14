import os
from urllib.parse import urlsplit


def write_file(name: str, file: str):
    if not os.path.exists(name):
        with open(name, 'w') as f:
            f.write(file + '\n')
    else:
        with open(name, 'a') as f:
            f.write(file + '\n')
    f.close()


def is_valid_url(url):
    try:
        result = urlsplit(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
