#!/bin/bash
apt update
apt install -y wireguard-tools resolvconf
cp /home/${USER}/wg0.conf /etc/wireguard/wg0.conf
chmod 600 /etc/wireguard/wg0.conf
wg-quick up wg0
