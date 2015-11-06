# coding=utf-8
__author__ = 'dracks'

import models
from Api.Manager import DataManager


def create(code, level, label_ca, label_es):
    warning_list = DataManager.sharedManager().retrieve_all('warning')
    for w in warning_list:
        if w.code == code:
            if w.name is None:
                w.name = {}
            w.level = level
            w.name['ca'] = label_ca
            w.name['es'] = label_es
            w.save()
            return

    w = models.Warnings()
    w.code = code
    w.level = level
    w.name = {'ca': label_ca}
    w.save()


def insert():
    create("MOT-1.1",3,u"Motivació inicial molt baixa",u"Motivación inicial muy baja")
    create("MOT-1.2",2,u"Portem uns dies amb motivació inicial baixa",u"Llevamos unos días con motivación inicial baja")
    create("MOT-1.3",2,u"La motivació inicial ha baixat en aquesta sessió",u"La motivación inicial ha bajado en esta sesión")
    create("MOT-1.4",2,u"La motivació inicial ha baixat en les dues últimes sessions",u"La motivación inicial ha bajado en las dos últimas sesiones")
    create("MOT-2.1",1,u"Ha baixat lleugerament la motivació inicial",u"La motivación inicial ha bajado ligeramente")
    create("MOT-3.1",2,u"Les sessions el desmotiven",u"Las sesiones lo desmotivan")
    create("MOT-3.2",2,u"La motivació ha baixat molt durant la sessió",u"La motvación ha bajado mucho durante esta sesión")
    create("MOT-3.3",1,u"S’ha desmotivat durant la sessió",u"Se ha desmotivado durante esta sesión")
    create("CL-1.1",2,u"És possible que s’estigui corregint a l’Older",u"Es posible que se esté corrigiendo al Older")
    create("CL-1.2",2,u"Detectem molts clics anòmals",u"Detectamos muchos clics anónimos")
    create("CL-1.3",1,u"Detectem clics anòmals",u"Detectamos clics anómalos")
    create("CL-2.1",1,u"La dificultat percebuda no s’ajusta amb la velocitat. Potser estem clicant malament",u"La dificultad percebida no se ajusta con la velocidad. Quizás están clicando mal")
    create("H-1.1",1,u"Pobrets, deixeu-los dormir!!!",u"¡Pobres, dejadlos dormir!")
    create("S-1.1",0,u"No s'ha fet la sessió.",u"No se ha hecho la sesión")
    create("P-1.1",4,u"Error de la pauta.",u"Error de la pauta")
    create("P-1.2",4,u"No hi ha més salts de block",u"No hay más saltos de block")
    create("P-1.3",4,u"No hi ha cap sessió feta",u"No hay ninguna sessión hecha")
    create("P-1.4",4,u"Número màxim de sessions pendents",u"Número máximo de sessiones pendientes")
    create("P-1.5",4,u"Sessions sense data de publicació",u"Sessiones sin fecha de publicación")
    create("P-1.6",4,u"No s'ha trobat el curs",u"No se ha encontrado el curso")
    create("SB-1.1",1,u"Salt de bloc amb normalitat",u"Salto de bloque normal")
    create("SB-1.2",1,u"Salt de bloc augmenant la dificultat",u"Salto de bloque aumentado la dificultad")
    create("SB-1.3",1,u"Salt de bloc disminuïnt un nivell la dificultat",u"Salto de bloque disminuyendo la dificultad un nivel")
    create("SB-1.4",2,u"Salt de bloc disminuïnt dos nivells la dificultat",u"Salto de bloque disminuyendo la dificultad dos niveles")
    create("SB-2.1",2,u"Entrem en un nivell per Olders amb dificultats",u"Entramos en un nivell para Olders con dificultades")
    create("SB-2.2",3,u"Entrem en un nivell per Olders amb moltes dificultats",u"Entramos en un nivell para Olders con muchas dificultades")

if __name__ == '__main__':
    #DataManager.sharedManager().set_config('config-beta.json')
    DataManager.sharedManager().get_all("warning")
    insert()
