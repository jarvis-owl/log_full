# @Author: scout
# @Date:   2018-03-04T10:54:16+01:00
# @Last modified by:   scout
# @Last modified time: 2018-03-24T11:15:40+01:00
# @License: GPL v3

'''
    this holds all functions used in main.py
'''


MIN = 1 #duration of data collection, see sleep for further resolution

import time
import mysql.connector as mariadb
import smbus
import Adafruit_DHT #> sudo python3 setup.py install >>> src: https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/software-install-updated
import numpy as np

#1-wire - drain this!
import os
import glob

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
    VERBOSE=False

    sleep=10
    duration=int((MIN*60) /sleep )
    temp=[]

    try:
        for i in range(duration):
            with open('/sys/class/thermal/thermal_zone0/temp','r') as f:
                temp.append( int( f.read() ) ) #readline
                f.close()

            time.sleep(sleep) #this should be increased, resolution unecessary

        if VERBOSE:
            print(temp)

        res=0
        #did not want to import numpy - oh you should have :P
        for index,element in enumerate(temp):
            res+=element

        que.put(int(res/len(temp) ) )
        #que.put(int(np.mean(temp)))

    except:
        print('[-] get core temp failed')
        return

def BMP_read(dummy,que):

    sleep=10
    duration=int( (MIN*60) /sleep )
    res_ap=[]
    res_t=[]

    for i in range(duration):

        try:
            #the following code was copied and not necessaily has to be understood

            # Distributed with a free-will license.
            # Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
            # BMP280
            # This code is designed to work with the BMP280_I2CS I2C Mini Module available from ControlEverything.com.
            # https://www.controleverything.com/content/Barometer?sku=BMP280_I2CSs#tabs-0-product_tabset-2


            # Get I2C bus
            bus = smbus.SMBus(1)

            # BMP280 address, 0x76(118)
            # Read data back from 0x88(136), 24 bytes
            b1 = bus.read_i2c_block_data(0x76, 0x88, 24)

            # Convert the data
            # Temp coefficents
            dig_T1 = b1[1] * 256 + b1[0]
            dig_T2 = b1[3] * 256 + b1[2]
            if dig_T2 > 32767 :
                dig_T2 -= 65536
            dig_T3 = b1[5] * 256 + b1[4]
            if dig_T3 > 32767 :
                dig_T3 -= 65536

            # Pressure coefficents
            dig_P1 = b1[7] * 256 + b1[6]
            dig_P2 = b1[9] * 256 + b1[8]
            if dig_P2 > 32767 :
                dig_P2 -= 65536
            dig_P3 = b1[11] * 256 + b1[10]
            if dig_P3 > 32767 :
                dig_P3 -= 65536
            dig_P4 = b1[13] * 256 + b1[12]
            if dig_P4 > 32767 :
                dig_P4 -= 65536
            dig_P5 = b1[15] * 256 + b1[14]
            if dig_P5 > 32767 :
                dig_P5 -= 65536
            dig_P6 = b1[17] * 256 + b1[16]
            if dig_P6 > 32767 :
                dig_P6 -= 65536
            dig_P7 = b1[19] * 256 + b1[18]
            if dig_P7 > 32767 :
                dig_P7 -= 65536
            dig_P8 = b1[21] * 256 + b1[20]
            if dig_P8 > 32767 :
                dig_P8 -= 65536
            dig_P9 = b1[23] * 256 + b1[22]
            if dig_P9 > 32767 :
                dig_P9 -= 65536

            # BMP280 address, 0x76(118)
            # Select Control measurement register, 0xF4(244)
            #		0x27(39)	Pressure and Temperature Oversampling rate = 1
            #					Normal mode
            bus.write_byte_data(0x76, 0xF4, 0x27)
            # BMP280 address, 0x76(118)
            # Select Configuration register, 0xF5(245)
            #		0xA0(00)	Stand_by time = 1000 ms
            bus.write_byte_data(0x76, 0xF5, 0xA0)

            time.sleep(0.5)

            # BMP280 address, 0x76(118)
            # Read data back from 0xF7(247), 8 bytes
            # Pressure MSB, Pressure LSB, Pressure xLSB, Temperature MSB, Temperature LSB
            # Temperature xLSB, Humidity MSB, Humidity LSB
            data = bus.read_i2c_block_data(0x76, 0xF7, 8)

            # Convert pressure and temperature data to 19-bits
            adc_p = ((data[0] * 65536) + (data[1] * 256) + (data[2] & 0xF0)) / 16
            adc_t = ((data[3] * 65536) + (data[4] * 256) + (data[5] & 0xF0)) / 16

            # Temperature offset calculations
            var1 = ((adc_t) / 16384.0 - (dig_T1) / 1024.0) * (dig_T2)
            var2 = (((adc_t) / 131072.0 - (dig_T1) / 8192.0) * ((adc_t)/131072.0 - (dig_T1)/8192.0)) * (dig_T3)
            t_fine = (var1 + var2)
            cTemp = (var1 + var2) / 5120.0
            fTemp = cTemp * 1.8 + 32

            # Pressure offset calculations
            var1 = (t_fine / 2.0) - 64000.0
            var2 = var1 * var1 * (dig_P6) / 32768.0
            var2 = var2 + var1 * (dig_P5) * 2.0
            var2 = (var2 / 4.0) + ((dig_P4) * 65536.0)
            var1 = ((dig_P3) * var1 * var1 / 524288.0 + ( dig_P2) * var1) / 524288.0
            var1 = (1.0 + var1 / 32768.0) * (dig_P1)
            p = 1048576.0 - adc_p
            p = (p - (var2 / 4096.0)) * 6250.0 / var1
            var1 = (dig_P9) * p * p / 2147483648.0
            var2 = p * (dig_P8) / 32768.0
            pressure = (p + (var1 + var2 + (dig_P7)) / 16.0) / 100

            res_ap.append(pressure)
            res_t.append(cTemp)
            time.sleep(sleep)

        except:
            print('[-] read BMP Sensor failed')
            res_ap.append(0)
            res_t.append(0)

    res=0
    #did not want to import numpy - still
    for index,element in enumerate(res_ap):
        res+=element

    que.put(res/len(res_ap) )
    #que.put(float(np.mean(res_ap)) )

    res=0
    for index,element in enumerate(res_t):
        res+=element

    que.put(res/len(res_t) )
    #que.put(float(np.mean(res_t)) )


def DHT_read(dummy,que):
    VERBOSE=False
    sleep=10

    sensor11 = Adafruit_DHT.DHT11
    pin11=23
    sensor22_1 = Adafruit_DHT.DHT22
    pin22_1=22
    sensor22_2 = Adafruit_DHT.DHT22
    pin22_2=27

    humidity11=[];   temperature11=[]
    humidity22_1=[];   temperature22_1=[]
    humidity22_2=[];   temperature22_2=[]


    duration=int((MIN*60) /sleep )
    for i in range(duration):
        try:
            tmp=Adafruit_DHT.read_retry(sensor11,pin11)
            humidity11.append(tmp[0])
            temperature11.append(tmp[1])

            tmp=Adafruit_DHT.read_retry(sensor22_1,pin22_1)
            humidity22_1.append(tmp[0])
            temperature22_1.append(tmp[1])

            tmp=Adafruit_DHT.read_retry(sensor22_2,pin22_2)
            humidity22_2.append(tmp[0])
            temperature22_2.append(tmp[1])

        except Exception as e:
            if VERBOSE:
                print('[-] read DHT failed'+str(e))
        time.sleep(sleep)

    #mysql cant handle np double
    que.put(float(np.mean(humidity11)) )
    que.put(float(np.mean(temperature11)) )
    que.put(float(np.mean(humidity22_1)) )
    que.put(float(np.mean(temperature22_1)) )
    que.put(float(np.mean(humidity22_2)) )
    que.put(float(np.mean(temperature22_2)) )

def onewire_read(dummy,que):
    '''this could be shortened''' '''was shortened'''

    res=[]
    # Finds the correct device file that holds the temperature data
    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'

    sleep=10
    duration=int( (MIN*60) /sleep )

    for i in range(duration):
        f = open(device_file, 'r') # Opens the temperature device file
        lines = f.readlines()
        f.close()
        line=lines[1]

        tmp_string = str( line[-5:])
        res.append( float(tmp_string.strip('\n')) / 1000.0 )
        #temp_f = temp_c * 9.0 / 5.0 + 32.0
        time.sleep(sleep)


    que.put(float(np.mean(res)) )


def emit_sql(unix=1521840837.0873652, datestamp='1970-01-01',timestamp='00:00:00',core_temp=99999,hum_11=11.0,temp_11=5.0,hum_22_1=99.1,temp_22_1=5.1,hum_22_2=99.2,temp_22_2=5.2,airpressure=9999.999,temp_bmp=5.5,temp_out=0.1,ping_ext=0.1,ping_loc=0.2):
    VERBOSE = False
    DB_NAME = 'test_database' #get better name - first release upcoming
    TB_NAME = 'logx' #same here
    user = []
    password = []

    with open('/home/pi/log_full/.credentials','r') as f:
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
    cursor.execute("CREATE TABLE IF NOT EXISTS "+TB_NAME+" (unix INT(10), datestamp TEXT(10), timestamp TEXT(8), core_temp INT(5), hum_11 DECIMAL(3,1), temp_11 DECIMAL(3,1), hum_22_1 DECIMAL(3,1), temp_22_1 DECIMAL(3,1), hum_22_2 DECIMAL(3,1), temp_22_2 DECIMAL(3,1), airpressure DECIMAL(6,3), temp_bmp DECIMAL(5,3), temp_out DECIMAL(5,3), ping_ext DECIMAL(3,2), ping_loc DECIMAL(3,2) ) ")

    # ============================= insert values ===========================
    cursor.execute("INSERT INTO logx (unix, datestamp,timestamp,core_temp,hum_11,temp_11,hum_22_1,temp_22_1,hum_22_2,temp_22_2,airpressure,temp_bmp,temp_out,ping_ext,ping_loc) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ",
                                     (unix, datestamp,timestamp,core_temp,hum_11,temp_11,hum_22_1,temp_22_1,hum_22_2,temp_22_2,airpressure,temp_bmp,temp_out,ping_ext,ping_loc) )

    # ================================ clean up =============================
    mariadb_connection.commit()
    if VERBOSE:
        print('from emit_sql: {}'.format(timestamp) )
