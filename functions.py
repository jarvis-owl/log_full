# @Author: scout
# @Date:   2018-03-04T10:54:16+01:00
# @Last modified by:   scout
# @Last modified time: 2018-03-04T19:42:21+01:00
# @License: GPL v3

'''
    this holds all functions used in main.py
'''


MIN = 1 #default 0.99

import time
import mysql.connector as mariadb

from subprocess import call,Popen,PIPE
from socket import gethostbyname


def ping_unix(host,que):
    VERBOSE = False

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
            print("[-] ping failed")
            #que.put(0) #None
            break

        time.sleep(1)


    #return ([n/(MIN*60),m/(MIN*60)] )
    try:
        if VERBOSE:
            print('[+] queue.put')
            print(count)
            print(duration)
        que.put(count/duration) #put complete result in queue
    except:
        if VERBOSE:
            print('[-] queue.put failed')
        pass

def get_core_temp(dummy,que):
    VERBOSE=True
    try:
        sleep=10
        duration=int((MIN*60) /sleep )
        temp=[]

        for i in range(duration):
            with open('/sys/class/thermal/thermal_zone0/temp','r') as f:
                temp.append( int( f.read() ) ) #readline
                f.close()

            #mom's spaghetti
            # if temp > 0:
            #     temp=int( (tmp+temp)/2 ) #make mean
            # else:
            #     temp=tmp


            time.sleep(sleep) #this should be increased

        if VERBOSE:
            print(temp)

        res=0
        #did not want to import numpy
        for index,element in enumerate(temp):
            res+=element

        que.put(int(res/len(temp) ) )
    except:
        print('[-] get core temp failed')
        return

def emit_sql(datestamp='1970-01-01',timestamp='00:00:00',core_temp=99999,hum_11=11.0,temp_11=5.0,hum_22_1=99.1,temp_22_1=5.1,hum_22_2=99.2,temp_22_2=5.2,airpressure=9999.999,temp_bmp=5.5,temp_out=0.1,ping_ext=0.1,ping_loc=0.2):
    VERBOSE = True
    DB_NAME = 'test_database'
    TB_NAME = 'logx'
    user = []
    password = []

    with open('.credentials','r') as f:
        user = f.readline()
        password = f.readline().strip()

    # ========================== set up connection =========================
    #connect to server with no database chosen
    mariadb_connection = mariadb.connect(host='localhost',user=user, password=password)
    cursor = mariadb_connection.cursor()

    #if exists choose test_database
    cursor.execute("CREATE DATABASE IF NOT EXISTS " + DB_NAME)
    mariadb_connection.commit()

    #connect to database
    mariadb_connection = mariadb.connect(host='localhost',user=user, password=password, database=DB_NAME)
    cursor = mariadb_connection.cursor()

    #if exists choose table
    cursor.execute("CREATE TABLE IF NOT EXISTS "+TB_NAME+" (datestamp TEXT(10), timestamp TEXT(8), core_temp INT(5), hum_11 DECIMAL(3,1), temp_11 DECIMAL(3,1), hum_22_1 DECIMAL(3,1), temp_22_1 DECIMAL(3,1), hum_22_2 DECIMAL(3,1), temp_22_2 DECIMAL(3,1), airpressure DECIMAL(6,3), temp_bmp DECIMAL(5,3), temp_out DECIMAL(5,3), ping_ext DECIMAL(3,2), ping_loc DECIMAL(3,2) ) ")

    # ============================= insert values ===========================
    cursor.execute("INSERT INTO logx (datestamp,timestamp,core_temp,hum_11,temp_11,hum_22_1,temp_22_1,hum_22_2,temp_22_2,airpressure,temp_bmp,temp_out,ping_ext,ping_loc) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ",
                                     (datestamp,timestamp,core_temp,hum_11,temp_11,hum_22_1,temp_22_1,hum_22_2,temp_22_2,airpressure,temp_bmp,temp_out,ping_ext,ping_loc) )

    # ================================ clean up =============================
    mariadb_connection.commit()
