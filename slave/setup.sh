#!/bin/bash

if (( $EUID != 0 )); then
    echo "@ERROR: Please run as root"
    exit
fi

BIN_PATH='/usr/local/bin/qcheckserv'

echo "@INFO: Installing qcheckserv"
if [ ! -d "${BIN_PATH}"  ]; then
    mkdir "${BIN_PATH}"
fi
cp ./.env_example "${BIN_PATH}/.env"
cp ./server_checker.py "${BIN_PATH}/"

echo "@INFO: Copying service files"
cp ./services/qcheckserv_server_checker.service /etc/systemd/system/
cp ./services/qcheckserv_server_checker.timer /etc/systemd/system/

echo "@INFO: Reloading services"
systemctl daemon-reload
systemctl start qcheckserv_server_checker.timer
systemctl status qcheckserv_server_checker.timer