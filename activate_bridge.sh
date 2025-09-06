#!/bin/bash

switch_list=$1

for elemento in $switch_list; do
    #creo il bridge
    ip link add $elemento type bridge
    #lo attivo
    ip link set $elemento up
done