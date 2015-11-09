__author__ = 'dracks'

import models
import main as program
from Api.EndpointModel import Model
from datetime import datetime, date
from dateutil import parser as date_parser
from Api.Manager import DataManager
import argparse


def mock_save(self):
    pass


def debug(config_id):

    program.load_cache()

    config = models.OlderConfig.get(config_id)
    monday = program.week_start_date()
    config.warnings = []
    monday = datetime.combine(monday, datetime.min.time())
    program.run(config, monday)
    config.save()


def debug_main(day=date.today()):
    program.load_cache()

    program.main(day)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', default=None, help="debug a configuration", metavar=("id_config",))
    parser.add_argument('-m', default=None, help="Run main configuration for a day", metavar=("day",))
    parser.add_argument('-c', default=None, help="Use file configuration", metavar=("config.json",))
    parser.add_argument('-s', default=False, action='store_true', help='Save the changes to the server, by default don\'t save it')

    args = parser.parse_args()
    if args.d and args.m:
        parser.error("Argument -m and -d are mutual exclusives")

    if args.c:
        DataManager.sharedManager().set_config(args.c)

    if not args.s:
        Model.save = mock_save

    if args.d:
        debug(args.d)
    elif args.m:
        debug_main(date_parser.parse(args.m))
    else:
        parser.error("You should select -m or -d options to run")