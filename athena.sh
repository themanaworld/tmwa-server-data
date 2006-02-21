#!/bin/bash

# $Id$
#----------------------------------------------------------------------
# Description: eAthena dameon control script.
# Author: Zuzanna K. Filutowska <platyna@platinum.linux.pl>
# Created at: Fri Feb 17 18:23:56 CET 2006
# License: GPL
# Copyright (c) 2006 Zuzanna K. Filutowska  All rights reserved.
#
#----------------------------------------------------------------------
# Configure section:
PATH=$PATH:.
SRVHOMEDIR=$HOME/tmwserver
#----------------------------------------------------------------------
# main()

cd ${SRVHOMEDIR}

athena_start() {
    if [ -x ${SRVHOMEDIR}/login-server ]; 
	then echo "Starting login server..."
	     ${SRVHOMEDIR}/login-server > ${SRVHOMEDIR}/log/login-server-startup.log 2>&1 &
	else echo "Login server binary is not executable or not found."
    fi
    
    if [ -x ${SRVHOMEDIR}/char-server ]; 
	then echo "Starting char server..."
	     ${SRVHOMEDIR}/char-server > ${SRVHOMEDIR}/log/char-server-startup.log 2>&1 &
	else echo "Character server binary is not executable or not found."
    fi

    if [ -x ${SRVHOMEDIR}/map-server ]; 
	then echo "Starting map server..."
	     ${SRVHOMEDIR}/map-server > ${SRVHOMEDIR}/log/map-server-startup.log 2>&1 &
	else
	    echo "Map server binary is not executable or not found."
    fi
}

athena_stop() {
    echo "Shutting down login server..."
    killall login-server
    echo "Shutting down char server..."
    killall char-server
    echo "Shutting down map server..."
    killall map-server
}

athena_restart() {
    athena_stop
    echo "Waiting for all processes to end..."
    sleep 10
    athena_start
}

case "$1" in
'start')
  athena_start
  ;;
'stop')
  athena_stop
  ;;
'restart')
  athena_restart
  ;;
*)
  echo "usage $0 start|stop|restart"
esac
