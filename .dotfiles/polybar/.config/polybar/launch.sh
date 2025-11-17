#!/bin/bash

#Terminating all other polybar instances
killall -9 polybar

#Wait unitl the process are shut down
while pgrep -u $UID -x polybar >/dev/null; do sleep 1; done

polybar example &

echo "Polybar launched..."

