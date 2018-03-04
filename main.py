# @Author: scout
# @Date:   2018-03-04T10:17:42+01:00
# @Last modified by:   scout
# @Last modified time: 2018-03-04T20:53:09+01:00
# @License: GPL v3

'''
    this holds the main procedures
'''

VERBOSE = False

from socket import *
import queue
from threading import *
import time
import datetime



#import platform
from functions import ping_unix,get_core_temp,emit_sql,BMP_read
PRESSURE=0

if __name__ == '__main__':

    # ============================ OBTAIN VALUES ============================
    #thread management:
    setdefaulttimeout(1)

    threads = []
    nb_threads = 8
    max_id = 945718

    #============================ set up queues =============================
    queues = []
    #number of queues could be reduced with storing key,value pair in one queue

    q_1 = queue.Queue() #will have only one element - ping ratio
    queues.append(q_1)

    q_2 = queue.Queue()
    queues.append(q_2)

    q_ct = queue.Queue()
    queues.append(q_ct)

    q_ap = queue.Queue()
    queues.append(q_ap)

    if True:
        print('collecting data ...')
    # ========================== =set up threads ============================
    #threading ping out
    thread_p1 = Thread(target=ping_unix,args=('www.duckduckgo.com',q_1) )
    threads.append(thread_p1)
    thread_p1.start()

    #threading ping loc
    thread_p2 = Thread(target=ping_unix,args=('fritz.box',q_2))
    threads.append(thread_p2)
    thread_p2.start()

    #threading core temp
    thread_ct = Thread(target=get_core_temp,args=('dummy',q_ct) )
    threads.append(thread_ct)
    thread_ct.start()

    #threading airpressure
    thread_ap = Thread(target=BMP_read,args=('dummy',q_ap) )
    threads.append(thread_ap)
    thread_ap.start()

    #=============================== join threads ============================
    if VERBOSE:
        print('#threads: '+str(len(threads)) )
    for thread in threads:
        try:
            thread.join()
            if VERBOSE: print(str(thread)+' joined')
        except:
            if VERBOSE:
                e = sys.exc_info()[0]
                print( "[-] join failed: %s" % e )


    #===================== retrieve return values from queues ================
    ping_loc = q_2.get() #was 0, but next lines are unecessary - queue size = 1, but would work, if < 1
    # for _ in range(q_2.qsize() ):
    #     tmp = q_2.get()
    #     #print(tmp,end='\n')
    #     pings_loc+=tmp
    q_2.task_done()

    ping_ext = q_1.get()
    q_1.task_done()

    core_temp=q_ct.get()
    q_ct.task_done()

    airpressure = q_ap.get()
    q_ap.task_done()

    temp_bmp = q_ap.get()
    q_ap.task_done()

    for que in queues:
        que.join()
        if VERBOSE: print(str(que)+' joined')

    datestamp=str(datetime.datetime.fromtimestamp(time.time() ).strftime('%Y-%m-%d') )
    timestamp=str(datetime.datetime.fromtimestamp(time.time() ).strftime('%H:%M:%S') )



    if VERBOSE:
        print('loc: {:1.2f} out: {:1.2f}'.format(ping_loc,ping_ext ) )
        print(core_temp)
        print(timestamp)
        print(airpressure)




    emit_sql(datestamp=datestamp,timestamp=timestamp,core_temp=core_temp,airpressure=airpressure,temp_bmp=temp_bmp,ping_ext=ping_ext,ping_loc=ping_loc)
