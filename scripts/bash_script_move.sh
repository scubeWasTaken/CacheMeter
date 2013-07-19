#!/bin/bash
SCRIPT=$(readlink -f $0)
SCRIPTPATH=$(dirname $SCRIPT)
echo $SCRIPTPATH/../data/requests/$1.request_raw
cp ~/Desktop/http-request-log.txt $SCRIPTPATH/../data/requests/$1.request_raw
echo "" > ~/Desktop/http-request-log.txt