#!/bin/bash

while true
do
  password=$(juju-run {{unit}} "config-get encfs-password")
  if [[ $? == 0 ]]; then
        break
  else
        sleep 1
  fi
done

echo "$password" | encfs -S --public /home/weechat/.encweechat /home/weechat/.weechat
