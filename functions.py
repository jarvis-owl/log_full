# @Author: scout
# @Date:   2018-03-04T10:54:16+01:00
# @Last modified by:   scout
# @Last modified time: 2018-03-04T14:44:11+01:00
# @License: GPL v3

'''
    this holds all functions used in main.py
'''

VERBOSE = True
MIN = 0.1 #default 0.99

from subprocess import call,Popen,PIPE
from socket import *
import time


def ping_unix(host,que):

    count=0
    duration=int(MIN*60)

    for i in range(duration):
        try:
            ping = Popen(["ping","-c1","-w1",str(gethostbyname(host) )],stdout = PIPE,stderr = PIPE )
            out, error = ping.communicate()
            #out = out.strip() #default is blank
            #error = error.strip()
            #if VERBOSE:
                #print(out)
                #print(error)
            if "0% packet loss" in str(out): #just one ping
                #return 1
                count+=1
                if VERBOSE:
                    print('[+] ping succeeded')


        except:
            if VERBOSE:
                print("[-] ping failed")
            #return 0
            pass

        time.sleep(1)


    #return ([n/(MIN*60),m/(MIN*60)] )
    try:
        if VERBOSE:
            print('[+] queue.put')
            print(count)
            print(duration)
        que.put(count/duration) #put complete result in queue
        #que.put(11)
        return
    except:
        if VERBOSE:
            print('[-] queue.put failed')
        return
