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
- [ ] implement logging
  - [x]  heartbeat
    - [x] threading
    - [x] queuing ([return values from threads](https://stackoverflow.com/questions/2577233/threading-in-python-retrieve-return-value-when-using-target))
  - [x]  core_temp
  - [ ]  DHT Sensors
  - [ ]  BMP Sensors
  - [ ]  1w Sensor
- [ ] show SQL on website
- [ ] build graphs from database
- coffee &#x2713; &#x2713;

---------------------------------------------------------------------------

## Prospect
- add further sensors
- validate plausible sensor values
- [check bandwidth](https://stackoverflow.com/questions/316866/ping-a-site-in-python/317206#317206) with RTT

## License
```
see LICENSE
 ```
