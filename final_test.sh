#!/bin/sh

#Test run for a demo client
a=`dig +short @cs5700cdnproject.ccs.neu.edu -p 63333 -n cs5700cdn.example.com`
echo $a
time wget http://$a:63333/
