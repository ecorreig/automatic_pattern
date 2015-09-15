__author__ = 'dracks'

import models
from Api.Manager import DataManager


def main():
    es = DataManager.sharedManager().query('language', 'es')
    print es
    print es.name
    print es.id
    patterns = models.Pattern.get()
    len(patterns)
    print(patterns[0].id)
    print(patterns[0].language.name)
    print(patterns[0].blocks)

    print (patterns[-1].id)
    print (patterns[-1].name)
    print (patterns[-1].language.name)

	"""
    nou = models.Pattern()
    nou.name = "Nou patro"
    nou.language = models.Language.get("es")
    nou.save()

    test = patterns[1]

    test.name = "Modificat from automatic pattern"
    test.save()

    newpattern = models.Pattern()
    newpattern.name = "New from python 2"
    newpattern.language = models.Language.get("ca")
    p = newpattern.save()

    print newpattern.id, p.id
    #"""

if __name__ == "__main__":
    main()
