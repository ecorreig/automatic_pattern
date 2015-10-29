__author__ = 'dracks'

import models
from Api.Manager import DataManager
import argparse


def main():
    list_history = models.PatternHistory.get(query='older=21032')
    for history in list_history:
        print history.pattern.name, history.day, history.block.name, history.level, \
            map(lambda e: e.code, history.warnings), \
            map(lambda s: s.name, history.sessions)


if __name__ == "__main__":
    #DataManager.sharedManager().set_config('config-beta.json')
    main()
