#!/bin/bash

if (( $EUID != 0 )); then
    echo "@ERROR: Please run as root"
    exit
fi

BIN_PATH='/usr/local/bin/qcheckserv'

if [ ! -d "${BIN_PATH}"  ]; then
    echo "@INFO: Installing qcheckserv"
else
    echo "@INFO: Updating qcheckserv"
    rm -rf "${BIN_PATH}/"
fi
mkdir "${BIN_PATH}"

if [ -f "${BIN_PATH}/.env" ]; then
    read -p "> .env file detected. Override with fresh? [y/N]" yn
    case $yn in
        [Yy]* ) echo "@INFO: Replacing config"; cp ./.env_example "${BIN_PATH}/.env"; break;;
        * ) echo "@INFO: Leaving old config";;
    esac
else
    cp ./.env_example "${BIN_PATH}/.env"
fi

cp ./server_checker.py "${BIN_PATH}/"

echo "@INFO: Copying service files"
cp ./services/qcheckserv_server_checker.service /etc/systemd/system/
cp ./services/qcheckserv_server_checker.timer /etc/systemd/system/

echo "@INFO: Reloading services"
systemctl daemon-reload
systemctl enable qcheckserv_server_checker.timer
systemctl start qcheckserv_server_checker.timer
systemctl status qcheckserv_server_checker.timer