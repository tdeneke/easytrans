#!/bin/sh

#kill all (worker, redis server and webserver)
ps axf | grep worker.py | grep -v grep | awk '{print "kill -9 " $1}' | sh
ps axf | grep redis-server | grep -v grep | awk '{print "kill -9 " $1}' | sh
ps axf | grep gunicorn | grep -v grep | awk '{print "kill -9 " $1}' | sh


#start all
redis-server redis.conf
gunicorn app:app -p rocket.pid -b 0.0.0.0:7788 -D
nohup ./worker.py &
