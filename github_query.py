import math
from urllib.parse import urlparse
import requests
import re

from uitl import GitPattern

RequestTimeOut = 3
QueryThreshold = 20


def github_query(repo):
    repo_language_api = transform_to_api(repo)
    if repo_language_api == '':
        return ''
    resp = requests.get(repo_language_api)
    if resp.status_code != 200:
        return

    language_map = resp.json()
    items = []
    total = 0
    for k in language_map:
        items.append((k, language_map[k]))
        total += language_map[k]

    items = [(k, math.ceil(language_map[k] / total * 100))
             for k in language_map]
    items = [(item[0], item[1]) for item in items if item[1] > QueryThreshold]
    return items


def transform_to_api(repo):
    ret = urlparse(repo)
    if ret.scheme == 'http' or ret.scheme == 'https':
        real_path = ret.path.removesuffix('.git')
        return 'https://api.github.com/repos%s/languages' % real_path
    else:
        x = re.match(GitPattern, repo)
        if x and x.group(2):
            return 'https://api.github.com/repos/%s/languages' % x.group(2)
    return ''


if __name__ == '__main__':
    ret = github_query('git@github.com:github/linguist.git')
    print(ret)
    ret = github_query('https://github.com/segmentio/asm.git')
    print(ret)