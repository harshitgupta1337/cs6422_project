#!/bin/bash

lat_stddev=0.0001
for N in 100
do
    for W in 2 4 8
    do
        for itt in 200 400 800 1600
        do
            for auto_rate in 0.00001
            do
                for lat_mean in 40
                do
                    echo "N=$N W=$W itt=$itt auto_rate=$auto_rate lat_mean=$lat_mean"
                    python3 single_controller_runner.py $N $W $itt $auto_rate 2 $lat_mean $lat_stddev
                    python3 system_simulator_runner.py $N $W $itt $auto_rate 1000 $lat_mean $lat_stddev
                done
            done
        done
    done
done
