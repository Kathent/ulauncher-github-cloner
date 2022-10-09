from asyncio.subprocess import STDOUT
import json
from os import path
import os
import subprocess
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent, PreferencesEvent, PreferencesUpdateEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

from github_query import github_query
from clipboard import clipboard_items
from logging import *

from languages import BaseLanguage, get_language, get_language_dir

BaseDir = ''
LanguageDirMap = {'go': 'go', 'rust': 'rust', "assembly": "asm"}
LanguageDirMapID = 'gg_language_dir'
BaseDirID = 'gg_base_dir'
IConMapID = 'gg_icon_map'


class GithubClonerExt(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterListener())
        self.subscribe(PreferencesEvent, PreferenceEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferenceUpdateEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        args = event.get_argument()
        items = []
        log(DEBUG, "get_argument args is: %s" % args)
        if not args:
            args_arr = clipboard_items()
            if not args_arr:
                return
            args = args_arr[0]
        log(DEBUG, "args is: %s" % args)
        github_query_items = github_query(args)
        for x in github_query_items:
            language = x[0].lower()
            store_dir = language
            if language in LanguageDirMap:
                store_dir = LanguageDirMap[language]
            language_obj = get_language(BaseDir, language)

            log(DEBUG, 'language icon is: %s' % language_obj.icon())
            items.append(
                ExtensionResultItem(icon=language_obj.icon(),
                                    name='%s %d%%' % (x[0], x[1]),
                                    description='',
                                    on_enter=ExtensionCustomAction({
                                        'repo':
                                        args,
                                        'store_dir':
                                        store_dir,
                                        'language':
                                        language
                                    })))
        return RenderResultListAction(items)


class ItemEnterListener(EventListener):

    def on_event(self, event, extension):
        log(DEBUG, 'on_event %s' % event.get_data())
        data = event.get_data()
        store_dir = data['store_dir']
        if not path.isabs(store_dir):
            store_dir = get_language_dir(BaseDir, data['store_dir'],
                                         data['repo'])

        proc = subprocess.run(["git", "clone", data['repo'], store_dir],
                              text=True,
                              capture_output=True)
        args = '%s %s %s %s' % ('git', 'clone', data['repo'], store_dir)
        log(DEBUG, 'args is: %s' % args)
        # proc = subprocess.run(["echo", args], text=True, capture_output=True)
        if proc.returncode != 0:
            return log(WARN, "clone repo fail, stdout: %s, stderr: %s",
                       proc.stdout, proc.stderr)
        log(DEBUG, 'git clone suc...')
        return super().on_event(event, extension)


class PreferenceEventListener(EventListener):

    def on_event(self, event, extension):
        global BaseDir, LanguageDirMap
        prefer = event.preferences
        if LanguageDirMapID in prefer:
            LanguageDirMap = json.loads(prefer[LanguageDirMapID])
        if BaseDirID in prefer:
            BaseDir = prefer[BaseDirID]
        if IConMapID in prefer:
            icon_map = json.loads(prefer[IConMapID])
            for x in icon_map:
                BaseLanguage.IconMap[x] = icon_map[x]
        log(DEBUG, 'IconMap is: %s' % str(json.dumps(BaseLanguage.IconMap)))
        return super().on_event(event, extension)


class PreferenceUpdateEventListener(EventListener):

    def on_event(self, event, extension):
        # log(DEBUG, "preference update is: %s, %s, %s " % (event.id, event.old_value, event.new_value))
        return super().on_event(event, extension)


if __name__ == '__main__':
    home_path = os.getenv('HOME')
    if home_path:
        BaseDir = path.join(home_path, 'workspace')
    GithubClonerExt().run()