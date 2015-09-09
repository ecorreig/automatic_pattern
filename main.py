__author__ = 'dracks'

import models


def main():
    es = models.Language.get('es')
    print es
    print es.name
    print es.id
    patterns = models.Pattern.get()
    print(patterns[0].id)
    print(patterns[0].language.get())
    print(patterns[0].blocks.get())
    print(patterns[1].language.get())
    print(patterns[1].blocks.get())


if __name__=="__main__":
    main()
