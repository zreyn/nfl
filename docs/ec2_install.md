EC2 Instance:
ec2-54-186-62-57.us-west-2.compute.amazonaws.com / 54.186.62.57
Security group allow TCP: 22, 80

---- On EC2 Instance ---
* git clone https://github.com/zreyn/nfl.git
* chmod +x nfl/src/install.sh
* nfl/src/install.sh
* tmux
* modify ip address in src/app.py
* sudo python src/app.py   

Note: this sudo is a really bad idea.  It's required to bind port 80, but we need to proxy Flask from EngineX.
