#!/bin/bash
python3 server.py &
sleep 5
python3 app.py &
sleep 5
xdg-open http://localhost:your_port_here
