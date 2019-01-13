#!/bin/bash

echo "$(juju-run {{unit}} "config-get encfs-password")" | encfs -S --public /home/weechat/.encweechat /home/weechat/.weechat
