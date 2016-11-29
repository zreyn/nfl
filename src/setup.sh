#!/bin/sh
git clone https://github.com/zreyn/nfl.git
chmod +x nfl/src/install.sh
nfl/src/install.sh
sudo python src/app.py   
