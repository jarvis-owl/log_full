# @Author: https://github.com/jarvis-owl <scout>
# @Date:   2018-03-20T09:25:55+01:00
# @Last modified by:   scout
# @Last modified time: 2018-03-20T09:26:04+01:00
# @License: GPL v3



#!bin/bash/

echo $(date --rfc-3339=seconds)
for ctl in "measure_clock arm" "measure_volts" "measure_temp"; do
        echo "$(vcgencmd $ctl)"
#       $ctl \t $(vcgencmd $ctl)
done
cat /sys/devices/virtual/thermal/thermal_zone0/temp
