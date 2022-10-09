from logging import DEBUG, WARNING, log
from os import path
import os

from uitl import repo_name, url_to_path


class BaseLanguage:
    IconMap = {'go': 'images/go.ico', 'rust': 'images/rust.svg'}

    def __init__(self, base_dir, language) -> None:
        self.language = language
        self.base_dir = base_dir

    def store_dir(self, repo):
        name = repo_name(repo)
        return path.join(self.base_dir, self.language.lower(), name)

    def icon(self):
        default_icon_path = 'images/icon.png'
        icon_path = 'images/%s.ico' % self.language
        if path.exists(icon_path):
            return icon_path
        if self.language in BaseLanguage.IconMap:
            return BaseLanguage.IconMap[self.language]
        return default_icon_path


class GoLanguage(BaseLanguage):

    def __init__(self, base_dir) -> None:
        super().__init__(base_dir, 'go')
        self.gopath = os.getenv('GOPATH')
        log(DEBUG, 'gopath is: %s' % self.gopath)
        if not self.gopath:
            self.gopath = path.join(self.base_dir, 'go', 'gopath')

    def store_dir(self, repo):
        repo_path = url_to_path(repo)
        repo_path = repo_path.removeprefix('/')
        if not repo_path:
            log(WARNING, 'not repo_path, repo: %s' % repo)
            return path.join(self.gopath, 'src')
        return path.join(self.gopath, 'src', repo_path)

    def icon(self):
        # icon_path = 'images/%s.ico' % self.language
        # if path.exists(icon_path):
        #     return icon_path
        return 'images/go.ico'


def get_language_dir(base_dir, language, repo):
    return get_language(base_dir, language).store_dir(repo)


def get_language(base_dir, language):
    if language.lower() == 'go':
        return GoLanguage(base_dir)
    return BaseLanguage(base_dir, language)


if __name__ == '__main__':
    repo = 'https://github.com/segmentio/asm.git'
    print(get_language_dir('/home/kathent/workspace', 'go', repo))
    repo = 'git@github.com:github/linguist.git'
    print(get_language_dir('/home/kathent/workspace', 'go', repo))