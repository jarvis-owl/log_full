# @Author: scout
# @Date:   2018-03-04T10:17:42+01:00
# @Last modified by:   scout
# @Last modified time: 2018-03-04T12:18:32+01:00
# @License: GPL v3

'''
    this holds the main procedures
'''

import datetime

#import platform
from functions import ping_unix


if __name__ == '__main__':
    #core_temp=call(["cat","/sys/class/thermal/thermal_zone0/temp"])
    [n_dix, n_router] = ping_unix() #this should probably be threaded
    with open('/home/pi/share/timestamps.log','a') as f:
        #f.write(' {0:.2f}'.format(ny))
        print('{} {}'.format(n_dix,n_router))
        f.close()
