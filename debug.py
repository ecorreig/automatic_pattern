__author__ = 'dracks'

import models
import main as program
from Api.EndpointModel import Model
from datetime import datetime
from Api.Manager import DataManager


def debug(config_id):
    def mock_save(self):
        pass

    Model.save = mock_save

    models.Course.get_all()
    models.Percentile.get()
    models.Warnings.get()

    config = models.OlderConfig.get(config_id)
    monday = program.week_start_date()
    monday = datetime.combine(monday, datetime.min.time())
    program.run(config, monday)


if __name__ == "__main__":
    DataManager.sharedManager().set_config('config-prod.json')
    debug("173")
    # models.Activity.get("2845759")


    """
    list = models.Session.get(query="student={older}&count=20".format(older=21034))
    for session in list:
        print session.model_based.id, session.status_begin
    """
