# @Author: scout
# @Date:   2018-03-04T10:17:42+01:00
# @Last modified by:   scout
# @Last modified time: 2018-03-24T17:01:36+01:00
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
from functions import ping_unix,get_core_temp,emit_sql,BMP_read,DHT_read,onewire_read


                        # TICTOCTICTOCTICTOCTICTOCTIC

if __name__ == '__main__':

    # ============================ OBTAIN VALUES ============================
    #thread management:
    setdefaulttimeout(1)

    t1 = time.time()
    threads = []
    nb_threads = 8
    max_id = 945718

    #============================ set up queues =============================
    queues = []
    #number of queues could be reduced with storing key,value pair in one queue

    q_1 = queue.Queue() #will have only one element - ping ratio
    queues.append(q_1) #ping extern

    q_2 = queue.Queue()
    queues.append(q_2) #ping local

    q_ct = queue.Queue()
    queues.append(q_ct) #rpi core temp

    q_bmp = queue.Queue()
    queues.append(q_bmp) #bmp airpressure and temp

    q_dht = queue.Queue()
    queues.append(q_dht) #{dht humidity and temperature }x3

    q_one = queue.Queue()
    queues.append(q_one) #1-wire temp sensor

    if VERBOSE:
        print('collecting data ...')
    # =========================== set up threads ============================
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
    thread_bmp = Thread(target=BMP_read,args=('dummy',q_bmp) )
    threads.append(thread_bmp)
    thread_bmp.start()

    #threading humidity
    thread_dht = Thread(target=DHT_read,args=('dummy',q_dht) )
    threads.append(thread_dht)
    thread_dht.start()

    #threading 1-wire
    thread_one = Thread(target=onewire_read,args=('dummy',q_one) )
    threads.append(thread_one)
    thread_one.start()

    #=============================== join threads ============================
    if VERBOSE:
        print('#threads: '+str(len(threads)) )
    for thread in threads:
        try:
            thread.join()
            if VERBOSE: print(str(thread)+' joined')
        except:

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

    airpressure = q_bmp.get()
    q_bmp.task_done()
    temp_bmp = q_bmp.get()
    q_bmp.task_done()

    try:
        if not q_dht.empty(): #this should be done for every queue.get()
            hum_11 = q_dht.get() #block=true,timeout=2) #boese - timeout too short for MIN
            q_dht.task_done()
            temp_11 = q_dht.get()
            q_dht.task_done()
            hum_22_1 = q_dht.get()
            q_dht.task_done()
            temp_22_1 = q_dht.get()
            q_dht.task_done()
            hum_22_2 = q_dht.get()
            q_dht.task_done()
            temp_22_2 = q_dht.get()
            q_dht.task_done()
        else:
            print('[-] q_dht empty')
    except:
        print('[-] q_dht failed')
        pass

    temp_out= q_one.get()#block=True,timeout=2) #here it worked - !?
    q_one.task_done()

    for que in queues:
        que.join()
        if VERBOSE: print(str(que)+' joined')

    #add unix timestamp
    unix = time.time()
    # v could be omitted
    datestamp=str(datetime.datetime.fromtimestamp(time.time() ).strftime('%Y-%m-%d') )
    timestamp=str(datetime.datetime.fromtimestamp(time.time() ).strftime('%H:%M:%S') )


    if VERBOSE:
        print('unix: {}'.format(unix) )
        print('datestamp: {}'.format(datestamp) )
        print('timestamp: {}'.format(timestamp) )
        print('core_temp: {}'.format(core_temp) )
        print('hum_11: {}'.format(hum_11) )
        print('temp_11: {}'.format(temp_11) )
        print('hum_22_1: {}'.format(hum_22_1) )
        print('temp_22_1: {}'.format(temp_22_1) )
        print('hum_22_2: {}'.format(hum_22_2) )
        print('temp_22_2: {}'.format(temp_22_2) )
        print('airpressure: {}'.format(airpressure) )
        print('temp_bmp: {}'.format(temp_bmp) )
        print('loc: {:1.2f} out: {:1.2f}'.format(ping_loc,ping_ext ) )



    emit_sql(unix=unix, datestamp=datestamp,timestamp=timestamp,core_temp=core_temp,hum_11=hum_11,temp_11=temp_11,hum_22_1=hum_22_1,temp_22_1=temp_22_1,hum_22_2=hum_22_2,temp_22_2=temp_22_2,airpressure=airpressure,temp_bmp=temp_bmp,temp_out=temp_out,ping_ext=ping_ext,ping_loc=ping_loc)
    print(time.time()-t1)
