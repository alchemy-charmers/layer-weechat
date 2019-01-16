# Overview

This charm provides [weechat][weechat]. Add a description here of what the service
itself actually does.

Also remember to check the [icon guidelines][] so that your charm looks good
in the Juju GUI.

# Usage

```bash
juju deploy cs:~pirate-charmesr/weechat
```

This will intsall weechat in a screen session. You can connect to the machine
and connect to the screen as the user 'weechat'.

```bash
juju ssh weechat/0
sudo su - weechat
screen -R
```

The charm also provides a reverseproxy relation which can be used with HAProxy.
If related to HAProxy the weechat relay will be available on HAProxy on port 443
URI /weechat. Weechat is setup with a self signed certificate which will be used
for the backend connection. HAProxy should also be configured with TLS.

# Configuration

See charm config options

# Contact Information

  - Upstream: https://github.com/pirate-charmers/layer-weechat
  - Bug tracker: https://github.com/pirate-charmers/layer-weechat/issues

[weechat]: https://weechat.org/
