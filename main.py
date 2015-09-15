__author__ = 'dracks'

import models
from Api.Manager import DataManager


def main():
    es = DataManager.sharedManager().query('language', 'es')
    print es
    print es.name
    print es.id
    patterns = models.Pattern.get()
    print(patterns[0].id)
    print(patterns[0].language.name)
    print(patterns[0].blocks)
    test = patterns[1]

    test.name = "Modificat from automatic pattern"
    test.save()

    newpattern = models.Pattern()
    newpattern.name = "New from python 2"
    newpattern.language = models.Language.get("ca")
    p = newpattern.save()

    print newpattern.id, p.id


if __name__ == "__main__":
    main()
