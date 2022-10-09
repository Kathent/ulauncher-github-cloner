from os import path
import re
from urllib.parse import urlparse

GitPattern = '^git@([^:]+):([^\/]+?\/.*?).git$'


def url_to_path(repo):
    ret = urlparse(repo)
    if ret.scheme == 'http' or ret.scheme == 'https':
        real_path = ret.path.removesuffix('.git')
        return ret.hostname + real_path
    else:
        x = re.match(GitPattern, repo)
        if x and x.group(1):
            return path.join(x.group(1), x.group(2))
    return ''


def repo_name(repo):
    ret = urlparse(repo)
    if ret.scheme == 'http' or ret.scheme == 'https':
        real_path = ret.path.removesuffix('.git')
        return path.basename(real_path)
    else:
        x = re.match(GitPattern, repo)
        if x and x.group(1):
            return path.basename(x.group(2))
    return ''