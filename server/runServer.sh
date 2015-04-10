#!/bin/bash
cd ~/COTS-Prototype/server/
uwsgi --http 192.168.1.103:5000 --wsgi-file server.py --callable app &
