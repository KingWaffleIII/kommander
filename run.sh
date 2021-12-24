#!/bin/bash

while getopts i:m:p:a: flag
do
	case "${flag}" in
		i) install=${OPTARG};;
		m) mode=${OPTARG};;
		p) port=${OPTARG};;
		a) api_port=${OPTARG};;
	esac
done

echo -e "\nThis script requires superuser privileges to restart Nginx for updates to static files to take effect.\n"
if [ "$(sudo -v)" == "Sorry, user $USER may not run sudo on $HOST" ]; then
	echo "\nYou have superuser permissions to use this script.\n"
	exit 1
fi

file="./kommander/settings.py"

if [ "$mode" == "dev" ]
then
	echo -e "\nDev flag supplied: enabling DEBUG...\n"

	from="DEBUG = False"
	to="DEBUG = True"
	sed -i "s/$from/$to/" $file

else
	echo -e "\nDev flag not supplied: disabling DEBUG...\n"

	from="DEBUG = True"
	to="DEBUG = False"
	sed -i "s/$from/$to/" $file
fi

if [ "$install" == "yes" ]
then
	echo -e "\nInstall flag supplied: installing dependencies...\n"

	npm --prefix ./api install

	python3.10 -m pip install -r ./requirements.txt
else
	echo -e "\nInstall flag not supplied: skipping installation of dependencies...\n"
fi

# define gunicorn
# GUNICORN=$(which gunicorn)
GUNICORN=/home/$USER/.local/bin/gunicorn

echo -e "\nPreparing...\n"

# make static dir for static files
if [ ! -d "./static" ]
then
	mkdir ./static
fi

# load static files
cp ./menshen/node_modules/xterm/lib/xterm.js ./app/static/app/
cp ./menshen/node_modules/xterm-addon-fit/lib/xterm-addon-fit.js ./app/static/app/
cp ./menshen/node_modules/socket.io/client-dist/socket.io.js ./app/static/app/socket.io/
cp ./menshen/node_modules/xterm/css/xterm.css ./app/static/app/

python3.10 manage.py makemigrations

python3.10 manage.py migrate

DJANGO_SETTINGS_MODULE=kommander.settings python3.10 init_sites.py

DJANGO_SUPERUSER_PASSWORD=4dm!nk3y! \
DJANGO_SUPERUSER_USERNAME=admin \
DJANGO_SUPERUSER_EMAIL=kingwaffl3iii@gmail.com \
python3.10 manage.py createsuperuser --no-input

echo $PASSWORD | sudo -S systemctl stop nginx

python3 manage.py collectstatic --no-input

echo $PASSWORD | sudo -S systemctl start nginx

echo -e "\nStarting the server...\n"

(trap 'kill 0' SIGINT EXIT; $GUNICORN --workers=2 --bind=0.0.0.0:$port kommander.wsgi & node menshen/server.js --port=$api_port)
