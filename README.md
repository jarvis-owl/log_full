<!--
@Author: scout
@Date:   2018-03-04T10:18:24+01:00
@Last modified by:   scout
@Last modified time: 2018-03-04T10:21:38+01:00
@License: GPL v3
-->



# Log
&nbsp;

A Python script to write acquired sensor data into SQL (MariaDB).

- [x] setup project / repository
- [x] setup MariaDB
- [x] implement logging
  - [x]  heartbeat
    - [x] threading
    - [x] queuing ([return values from threads](https://stackoverflow.com/questions/2577233/threading-in-python-retrieve-return-value-when-using-target))
  - [x]  core_temp
  - [x]  DHT Sensors
  - [x]  BMP Sensors
  - [x]  1w Sensor
- [ ] show SQL on website
- [ ] build graphs from database
- coffee &#x2713; &#x2713;
- tea  ||

# Appearances
- sometimes no INSERT is emitted - a DROP DATABASE relieves - to be investigated
- ~~make sleep global?~~ bad practice - make it a call parameter *(silly you)*
- eventually the sleep for the DHT Sensors should be increased
- I'm not very satisfied with the unique queues per task. Is there a better way?
- future me - do you understand the code? -> *comments*
- call parameters are */would be* nice for testing

---------------------------------------------------------------------------

## Prospect
- add further sensors
- validate plausible sensor values
- [check bandwidth](https://stackoverflow.com/questions/316866/ping-a-site-in-python/317206#317206) with RTT
- use LOG
- log the time a run really takes (tic,toc)
- log unix timestamp

## License
```
see LICENSE
 ```
