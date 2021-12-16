from gevent import monkey
monkey.patch_all()

import multiprocessing
debug = True
loglevel = 'debug'
bind = '0.0.0.0:9001'           # assign the IP and port of the WSGI server
pidfile = 'log/gunicorn.pid'    # should have a directory called "log" under the same directory
logfile = 'log/debug.log'
workers = multiprocessing.cpu_count() * 2 + 1    # number of worker processes (2 * cores + 1 as recommended)
worker_class = 'gevent'         # use async workers