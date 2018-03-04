# @Author: scout
# @Date:   2018-03-04T10:17:42+01:00
# @Last modified by:   scout
# @Last modified time: 2018-03-04T14:46:21+01:00
# @License: GPL v3

'''
    this holds the main procedures
'''

VERBOSE = True
import time
import sys

import datetime
from threading import *
from socket import *
import queue

#import platform
from functions import ping_unix


if __name__ == '__main__':
    #core_temp=call(["cat","/sys/class/thermal/thermal_zone0/temp"])

    setdefaulttimeout(1)

    threads = []
    nb_threads = 8
    max_id = 945718
    q_1 = queue.Queue() #will have only one element - ping ratio
    q_2 = queue.Queue()


    #[n_dix, n_router] = ping_unix() #this should probably be threaded

    #threading ping
    thread_p1 = Thread(target=ping_unix,args=('www.duckduckgo.com',q_1) )
    threads.append(thread_p1)
    thread_p1.start()

    thread_p2 = Thread(target=ping_unix,args=('fritz.box',q_2))
    threads.append(thread_p2)
    thread_p2.start()

    print('#threads: '+str(len(threads)) )
    #time.sleep(8)
    for thread in threads:
        try:
            thread.join()
        except:
            if VERBOSE:
                e = sys.exc_info()[0]
                print( "[-] join failed: %s" % e )

    # thread_p1.join()
    # thread_p2.join()

#evaluate pings
    #sum pings up
    print("size q_1: "+str(q_1.qsize() ) )
    print("size q_2: "+str(q_2.qsize() ) )

    pings_loc = 0
    for _ in range(q_2.qsize() ):
        tmp = q_2.get()
        print(tmp,end='')
        pings_loc+=tmp

    q_2.task_done()

    pings_out = 0
    for _ in range(q_1.qsize() ):
        tmp = q_1.get()
        pings_out+=tmp

    q_1.task_done()

    q_1.join()
    q_2.join()

    if VERBOSE:
        print('{} {}'.format(pings_loc,pings_out ) )
        #write in sql later

    with open('/home/pi/share/timestamps.log','a') as f:
        #f.write(' {0:.2f}'.format(ny))
        #print('{} {}'.format(n_dix,n_router))
        f.close()
