# Job Searching and Management Platform
Any comments and advices are welcomed!
_(For the detailed documentation, click [here](/doc))_

## Overview
This project aims to design a simple job searching website. It provides users with up-to-date job post information and supports job searching and filtering. It also allows companies to post and manage new job opportunities decently. The resources are collected from [Indeed](https://sg.indeed.com/?r=us). The developer hopes to realize similar functions as a normal job searching website.

## Structure Outline
This project is built up with 4 important components, which can be listed as follows:
* __web crawler:__ used to collect job posts from Indeed routinely
* __front-end UI:__ provide user interfaces for job searching and result displaying
* __back-end API:__ realize the logic for web pages, retrieve and proceed with user inputs while interact with databases to collect and return the results
* __databases__: used to store all the useful information (roles, users, jobs, etc.) and provide quick searches for job posts.

Meanwhile, the job searching platform generally provides the following functions:
* job posts searching platform open to any users (registered or unregistered); the page also supports post-searching operations like filtering and sorting;
* registration and logging in for users;
* a simple recommendation of jobs for users based on searching histories when no search is conducted;
* creation and management of job posts specified for companies;
* management of users specified for administrators.

## Infrastructure
The overall project is written in __Python__, and supported by __Flask__.

The web crawler uses Selenium to retrieve the static / dynamic contents from the original website. Once the contents are collected, they are proceeded locally with Beautiful Soup (bs4).

The front-end pages are displayed as html files with CSS styles. Bootstrap is chosen for page rendering. The results of interaction between front-end and back-end APIs are reflected in web pages with the help of Jinja2 template rendering engine, which is provided by Flask.

The back-end logics are realized with Flask, a lightweight Python framework. The visiting activities are recorded by cookies and sessions, and the sessions are stored in __Redis__.

Apart from the use of Redis, two types of database systems are applied in this project. __MySQL__ is selected for storing all the detailed information, including roles, accounts and job posts (forward indexed). Sqlalchemy is applied to interact with MySQL through Python script. Meanwhile, since the main function of a job searching site is the search for jobs, __Elasticsearch__ is adopted to support inverted indexing of the job posts in order to accelerate the searching process. 

## Installation and Deployment (only for _reference_)
* This instruction guide bulids up the project on Ubuntu OS.
### Step 0: update Linux resources
```
sudo apt update
sudo apt upgrade
```
### Step 1: install MySQL (see [more](https://dev.mysql.com/doc/mysql-apt-repo-quick-guide/en/))
* (for centOS, please follow [[1]](https://www.mysqltutorial.org/install-mysql-centos/), [[2]](https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/linux-installation-yum-repo.html))
```
sudo apt install mysql-server     # install mysql server
sudo mysql_secure_installation utility    # more configs upon installation (also sets up the root password)
sudo systemctl start mysql / service mysql start    # start service (check working status: systemctl status mysql)
sudo systemctl enable mysql    # launch at reboot
sudo mysql -uroot -p    # connect to mysql client
(under root user) create database search_engine;    # database used by the project
(under root user) create user 'dev'@'localhost' identified by 'your password';
(under root user) grant all privileges on search_engine.* to 'dev'@'localhost';
```
### Step 2: install ElasticSearch (see [more](https://www.elastic.co/guide/en/elasticsearch/reference/7.16/targz.html))
```
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.16.0-linux-x86_64.tar.gz
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.16.0-linux-x86_64.tar.gz.sha512
shasum -a 512 -c elasticsearch-7.16.0-linux-x86_64.tar.gz.sha512    # see notice
tar -xzf elasticsearch-7.16.0-linux-x86_64.tar.gz
cd elasticsearch-7.16.0/    # This directory is known as $ES_HOME
./bin/elasticsearch    # run ES
```
* _Notice_: Compares the SHA of the downloaded .tar.gz archive and the published checksum, which should output “elasticsearch-{version}-linux-x86_64.tar.gz: OK.”
* _Problem 1_: Killed upon start: change JVM heap size to no more than half of the available memory: go to ./config/jvm.options.d, create a new jvm.options file and add “-Xms[size]”, “-Xmx[size]”.
* _Problem 2_: cannot run elasticsearch as root user: 1) add a new user: adduser [user_name] (named as “elasticsearch” for the project), setup the passwords and other configs; 2) grant permission of elasticsearch to the new user: chown -R [user_name] [elasticsearch_directory]; 3) change from root to the new user: su [user_name]. Try again and hopefully everything would work.
### Step 3: install Redis
```
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make
sudo make install    # copy both the Redis server and the command line interface into the proper places
start Redis Server: redis-server
use Redis Client: redis-cli
```
* _Notice_: Might also have to install make, gcc and pkg-config
* _Problem 1_: jemalloc error: replace `make` with `make distclean && make`, which will clear the previous residual files
### Step 4: retrieve project recourses and install packages
```
sudo apt install git 
git clone https://github.com/AlanZhl/Job-Searching-Management-Platform.git
cd Job-Searching-Management-Platform
sh pipinstall.sh    # install all necessary Python packages
```
### Step 5: WSGI server configs (Gunicorn)
* (backend API and related supports should be installed in Step 4) All the configurations are included in /gconfig.py. Please modify according to your own settings and requirements.
Please create an empty folder "log" under the project directory, which is required by Gunicorn.
```
gunicorn -c gconfig.py serve:app    # create master and worker processes under Gunicorn
```
### Step 6: Reverse Proxy server configs (Nginx)
```
apt install nginx
cd /etc/nginx/conf.d
touch gunicorn.conf    # add configs for the WSGI server (rename according to your settings)
```
In `gunicorn.conf`, add at least the following configs:
```
server {
        listen 5001;               # Should not conflict with Nginx default port (80).
        server_name 172.17.0.2;    # Simply a name. Good to be aligned with the WSGI server IP.
        location / {
            proxy_pass http://0.0.0.0:9001;    # the socket bound by WSGI server.
        }
}
```
For reloading and management of the Nginx service:
```
nginx -s reload
service nginx start / stop / status
```
Finally, you could open the port listened to by Nginx server (5001 in this example) on the deployed remote server machine, and feel free to visit the project~