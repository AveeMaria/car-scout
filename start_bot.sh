#!/bin/bash

#preventiva
/usr/bin/pkill chrome
/usr/bin/pkill chromedriver
sleep 2

cd /home/uwu/car-scout

#clear log
> /home/uwu/car-scout/bot.log

#start python virtual env
/bin/bash -c "source /home/uwu/car-scout/selenium-env/bin/activate && /home/uwu/car-scout/selenium-env/bin/python /home/uwu/car-scout/bot.py >> /home/uwu/car-scout/bot.log 2>&1"