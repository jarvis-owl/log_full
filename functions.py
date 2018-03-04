# @Author: scout
# @Date:   2018-03-04T10:54:16+01:00
# @Last modified by:   scout
# @Last modified time: 2018-03-04T12:21:54+01:00
# @License: GPL v3

'''
    this holds all functions used in main.py
'''

VERBOSE = True
MIN = 0.99

from subprocess import call,Popen,PIPE
from socket import *
import time


def ping_unix():
    n = 0
    m = 0
    def ping(host_sub):
        try:
            ping = Popen(["ping","-c1","-w1",str(gethostbyname(host_sub) )],stdout = PIPE,stderr = PIPE )
            out, error = ping.communicate()
            #out = out.strip() #default is blank
            #error = error.strip()
            #if VERBOSE:
                #print(out)
                #print(error)
            if "0% packet loss" in str(out): #just one ping
                return 1
        except:
            print("[-]")
            return 0

    for i in range(int(MIN*60) ):
        n+=ping('www.duckduckgo.com')
        m+=ping('fritz.box')
        if VERBOSE:
            print(n)
        time.sleep(1)

    return ([n/(MIN*60),m/(MIN*60)] )
