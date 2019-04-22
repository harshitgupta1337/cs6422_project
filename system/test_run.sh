#!/bin/bash
python3 controller.py --conf conf/conf1.yaml > controller.out 2>&1 &
controller_pid=$!

sleep 1

python3 server.py --conf conf/server_0.yaml > server_0.out 2>&1 &
server_0_pid=$!
python3 server.py --conf conf/server_1.yaml > server_1.out 2>&1 &
server_1_pid=$!

sleep 1

python req_gen.py --url tcp://127.0.0.1:40000 --controller-url tcp://127.0.0.1:50000

kill $controller_pid
kill $server_0_pid
kill $server_1_pid

