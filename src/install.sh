# from the nfl directory
sudo apt-get update
sudo apt-get install python-setuptools python-dev build-essential
sudo apt-get install python-pip
sudo apt-get install nginx
sudo apt-get install tmux
sudo pip install --upgrade pip
sudo pip install requests
sudo pip install pandas
sudo pip install scikit-learn
sudo apt-get install python-numpy python-scipy
sudo pip install Flask
sudo pip install uwsgi
sudo pip install virtualenv
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10

virtualenv nflenv
source nflenv/bin/activate
pip install scipy scikit-learn pandas numpy requests Flask
deactivate

sudo cp nfl.conf /etc/init/.
sudo cp nfl_nginx /etc/nginx/sites-available/nfl
sudo ln -s /etc/nginx/sites-available/nfl /etc/nginx/sites-enabled

