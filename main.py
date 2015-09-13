__author__ = 'dracks'

import models


def main():
    es = models.Language.get('es')
    print es
    print es.name.get()
    print es.id.get()
    patterns = models.Pattern.get()
    print(patterns[0].id.get())
    print(patterns[0].language.get())
    print(patterns[0].blocks.get())
    #print(patterns[1].language.get())
    #print(patterns[1].blocks.get())
    test = patterns[0]

    test.name.set("Hola holita")
    test.save()

    newpattern = models.Pattern()
    newpattern.name.set("New from python")
    newpattern.language.set(es)
    p=newpattern.save()

    print newpattern.id.get(), p.id.get()



if __name__=="__main__":
    main()
