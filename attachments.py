from Api.Manager import DataManager

__author__ = 'dracks'

import models
import csv, os

def main():
    DataManager.sharedManager().set_config('config-prod.json')
    list_attachments=models.Attachment.get_all()
    writer=csv.writer(os.sys.stdout)
    for attachment in list_attachments:
        category = ""
        try:
            #print attachment.id.get(), attachment.category.get().name.get()
            category = attachment.category.name
        except:
            pass
        writer.writerow([category.encode('UTF-8', 'replace'), attachment.name.encode('UTF-8', 'replace'),
                         "/comment/attachment/"+attachment.id, attachment.description.encode('UTF-8', 'replace')])


if __name__=='__main__':
    main()