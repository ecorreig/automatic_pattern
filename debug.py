__author__ = 'dracks'

import models
import main as program
from Api.EndpointModel import Model
from datetime import datetime, date
from dateutil import parser
from Api.Manager import DataManager


def mock_save(self):
    pass


def debug(config_id):
    # Model.save = mock_save

    program.load_cache()

    config = models.OlderConfig.get(config_id)
    monday = program.week_start_date()
    config.warnings = []
    monday = datetime.combine(monday, datetime.min.time())
    program.run(config, monday)
    config.save()


def debug_main(day=date.today()):
    Model.save = mock_save
    program.load_cache()

    program.main(day)


if __name__ == "__main__":
    # DataManager.sharedManager().set_config('config-beta.json')
    # debug("14")

    debug_main(parser.parse("2015/11/09"))
