__author__ = 'dracks'

import models
from Api.Manager import DataManager
import datetime 
from datetime import date, timedelta
from operator import attrgetter


def test():
    es = DataManager.sharedManager().query('language', 'es')
    print es
    print es.name
    print es.id
    patterns = models.Pattern.get()
    print (patterns[0].name)
    len(patterns)
    #print(patterns[0].id)
    #print(patterns[0].language.name)
    print(patterns[0].blocks)

    #print (patterns[-1].id)
    #print (patterns[-1].name)
    #print (patterns[-1].language.name)
#    nou.language = models.Language.get("es")
#    nou.save()
"""
    test = patterns[1]

    test.name = "Modificat from automatic pattern"
    test.save()

    newpattern = models.Pattern()
    newpattern.name = "New from python 2"
    newpattern.language = models.Language.get("ca")
    p = newpattern.save()

    print newpattern.id, p.id
    #"""





"""
for configuration in older_pattern_relation:
   if configuration.runsToday:
       sessions_pendents=obte_sessions_pendents(configuration.older)
		sessions_pendents=configuration.num_sessions
		mentres sessions_pendents.length<configuration.num_sessions*2 && sessions_pendents>0:
        sessions_pendent--;
		next_session=configuracio.seguent_sessio()
        pujar_sessio(older, next_session)
"""
def day_week():
    #retorna el dia de setmana
    weekdays = {0:'monday', 1:'tuesday', 2:'wednesday', 3:'thursday', 4:'friday', 5:'saturday', 6:'sunday'}
    return weekdays[datetime.datetime.today().weekday()] 


def week_start_date(d=datetime.datetime.today()):  
    return d - timedelta(d.weekday())



def next_session(list_sessions, position, level, older):
    if (position < len(list_sessions)):					#si no es la utima sessio del bloc
        position+=1
        older.session=list_sessions[position]
    else:												#canvi de bloc
       block_jump=models.blockJump.get(query="block_jump={jump}".format(jump=older.block.block_jump))
       




def main():
    today= day_week()																				#guardem el nom del dia actual
    llista_olders= models.OlderConfig.get()															#Llista tots els olders disponibles
    monday=week_start_date()

    for older in llista_olders:
        working=older.workingDays
        if (getattr(working, today)):
            block=older.block
            level=older.level
            session=older.session
            list_block_sessions=filter(lambda e: e.level==level, block.sessions)							#llistat de sessions al bloc (amb atributs)
            list_block_sessions=sorted(list_block_sessions, key=attrgetter('order'))
            list_sessions=map(lambda e: e.session, list_block_sessions)										#llistat id_sessions del bloc
            #position=list_sessions.index(session)


            sessions=models.Session.get(query="student={older}&size=20".format(older=older.older))
            not_done_list=filter(lambda e: e.completed_time is not None,sessions)					#sessions no fetes
            not_done=len(not_done_list)
            sessions_block=filter(lambda e: e.model_based in list_sessions, not_done_list)
            not_done_pattern=len(sessions_block)
            sessions_week= filter(lambda e: e.publish_date>= str(monday) , sessions)
            s_week=len(sessions_week)
            cont=older.numberSessions

            while (not_done_pattern < 2*older.numberSessions and s_week<older.maxSessionWeek and not_done<10 and cont>0): 
                new_session=model.Session()
                new_session.student=older.older
                new_session.publishDate=datetime.datetime.today()
                new_session.modelBased=older.session
                new_session.save()

                #actualitzar older
                older.session=next_session(list_block_sessions, position, level, older)
                not_done_pattern+=1
                s_week+=1
                not_done+=1
                cont-=1
            
            #pattern_id= (older.pattern.name)
            #print ('Fa servir la Pauta: %s' ) %pattern_id


def prova():
    older=1
    sessions=models.Sessions.get(query="student=?&size=20, array(1)")
    print(sessions[0].creation_time)
    
    




if __name__ == "__main__":
   main()
