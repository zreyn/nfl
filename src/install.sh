# from the nfl directory, install some resources
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

# setup a virgual env and install what we need
virtualenv nflenv
source nflenv/bin/activate
pip install scipy scikit-learn pandas numpy requests Flask uwsgi

# you can test uwsgi and the app with:
# uwsgi --socket 0.0.0.0:8000 --protocol=http -w wsgi:nfl 

deactivate

# put some files where they need to be for nginx
sudo cp nfl.conf /etc/init/.
sudo cp nfl_nginx /etc/nginx/sites-available/nfl
sudo ln -s /etc/nginx/sites-available/nfl /etc/nginx/sites-enabled 

# start up the server
sudo cp nfl.service /etc/systemd/system/. 
sudo service nfl start
sudo service nginx restart
