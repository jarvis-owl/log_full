# @Author: scout
# @Date:   2018-03-04T10:54:16+01:00
# @Last modified by:   scout
# @Last modified time: 2018-03-04T20:52:02+01:00
# @License: GPL v3

'''
    this holds all functions used in main.py
'''


MIN = 5 #default 0.99

import time
import mysql.connector as mariadb
import smbus

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
    VERBOSE=False

    sleep=10
    duration=int((MIN*60) /sleep )
    temp=[]

    try:
        for i in range(duration):
            with open('/sys/class/thermal/thermal_zone0/temp','r') as f:
                temp.append( int( f.read() ) ) #readline
                f.close()

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

def BMP_read(dummy,que):

    sleep=10
    duration=int((MIN*60) /sleep )
    res_ap=[]
    res_t=[]

    for i in range(duration):

        try:
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

        except:
            print('[-] read BMP Sensor failed')
            res_ap.append(0)
            res_t.append(0)

    res=0
    #did not want to import numpy - still
    for index,element in enumerate(res_ap):
        res+=element

    que.put(res/len(res_ap) )

    res=0
    for index,element in enumerate(res_t):
        res+=element

    que.put(res/len(res_t) )
