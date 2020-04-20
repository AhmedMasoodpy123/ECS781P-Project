# ECS781P-Project

This repository contains a discussion forum with rest API service to get current local temperature for London. The application utilises a GET method to get the temperature from the public api but can only access this information with access to a private key.

The code from mydb establishes a connection to the RDS db through MySQL which allows the user to post into the relevant tables found in RDS. Once we have established the connection, one can use SQL queries to access posts and replies. One table is a topic table that includes the subject of the topic and the other table is a reply that needs to be linked with topic through use of the topic id as a primary key in the topic table and a foreign key in this reply table. One first gets the topics and orders them by topic id.

There are two commands within the page in regards to topic. The first command allows one can post a new topic which allows one to create a new topic form (see def new_topic) where one can define the subject and content. This utlises an SQL INSERT command to insert the topic subject and content into the topic table which is automatically assigned a topic_id. The topic_id is a dynamic variable which depends on the most recent topic posted.

The second command allows one to view recently posted topics (see def_view topic) which allows one to implement an SQL SELECT query to select the relevant topic based on the topic_id being equivalent to the topic selected. def query_db allows one to run a select query on the database and store values as a key value pair when the key is the column name and the value is the actual value of that column.

RDS allows one to have multiple databases and for this project, I created the database using the MYSQL Engine. This specific database allows information to only be accessed by the EC2 instance that I have run as well as the default port 0.0.0.0/0.

For the topics table, one utilises a select method to abstract the topic id and subject in question. One advantage of this dictionary is that one can access the values by simply giving the name of the columns rather than hard coded values i.e. [0],[1].

Within the login method, it firsts the checks the posted username against usernames and passwords within the database login. If the usernames match the database, the database login sends the relevant password and hashkey associated with the username to the SQL server. To check if the password entered by the user and the password accessed from the database match, the application utilising a hash based authentication. The advantage of hash functions that they cannot be decrypted even if the hacker has the hash key or has access to the database, as the hacker will not be able to access the users password, meaning that they are very secure. For hash based authentication, the application will take the password that the user has inputed and the hashkey abstracted from the database, and encrypt them. If the encryption matches what is found in the original database, then the user will be let into the page.


**Create a virtual environment which will act as a source for all libraries of python**

```
virtualenv flask-forum
source flask-forum/bin/activate
```

In order to install the pre-requisites run the following command:
```
pip3 install -r requirements.txt
```

This will add all the packages to your local virtual environment.

Before we can run it we need to execute mysql script for which RDS AWS service was used.

```
DROP TABLE IF EXISTS `login`;
CREATE TABLE IF NOT EXISTS `login` (
  `id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `hash_key` varchar(255) NOT NULL
) 
INSERT INTO `login` (`id`, `username`, `password`, `hash_key`) VALUES

(0, 'admin', '$2b$12$t7nvrHdSQnlYF9WwJFuLCOMc1XGTGw/SVrWFIG7M/fJllsUULC5b6', 
 '$2b$12$t7nvrHdSQnlYF9WwJFuLCO');

DROP TABLE IF EXISTS `topic`;
CREATE TABLE IF NOT EXISTS `topic` (
  `topic_id` int(11) NOT NULL AUTO_INCREMENT,
  `subject` varchar(255) NOT NULL,
  PRIMARY KEY (`topic_id`)
) 
DROP TABLE IF EXISTS `claim`;
CREATE TABLE IF NOT EXISTS `claim` (
  `claim_id` int(11) NOT NULL AUTO_INCREMENT,
  `content` varchar(255)  NOT NULL,
  `time` int(11) NOT NULL,
  `author` varchar(255) NOT NULL,
  `topic_id` int(11) NOT NULL,
  PRIMARY KEY (`claim_id`)
)
```
Change the mysql credentials in project.py

Now in order to run the server you can use the following command:
```
python project.py
```
This will start the server at default 5000 port and you can test.

In order to use WSGI file listening at port project.sock inside project.ini file and use an nginx server the following configuration of nginx is required:
```
server {
    listen 80;
    server_name 35.153.70.175;
   location / {
        include uwsgi_params;
        uwsgi_pass unix:/home/ubuntu/project/project.sock;
    }
}
```
This will configure nginx and inorder to add the python environment we use the following script to create a script in the system

[Unit]
Description=uWSGI instance to serve project
After=network.target
[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/project
Environment=/home/ubuntu/project/flask-forum/bin/activate
ExecStart=/home/ubuntu/.local/bin/uwsgi --ini project.ini

[Install]
WantedBy=multi-user.target


This will configure a nginx server which can be started by command

sudo service nginx start

And allows to use a domain ip to access the server.

Once we have this we need to configure kuberntes and use scaling.

The commands are as follows:

microk8s.kubectl create deployment project --instance=nginx

This will create a deployment and to use load balancer run the following command.

microk8s.kubectl expose deployment/project --type="LoadBalancer" --port 80

microk8s.kubectl get pods

microk8s.kubectl get services

kubectl describe services/project

kubectl get services -l run=nginx

kubectl scale deployment project --replicas=5

This will create 5 replicas and use load balancer.
