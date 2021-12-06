#!/bin/bash
for last; do true; done

spotifyd_config="/etc/default/spotifyd"

if [[ $last == "on" ]]; then
    sudo sed -i -E "s/^#username = /username = /" $spotifyd_config
    sudo sed -i -E "s/^#password = /password = /" $spotifyd_config
	echo "linked"
else
    sudo sed -i -E "s/^username = /#username = /" $spotifyd_config
    sudo sed -i -E "s/^password = /#password = /" $spotifyd_config
	echo "unlinked"
fi

sudo service spotifyd restart

