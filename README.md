# ECS781P-Project
## Discussion Forum that also provides the local temperature for London.

The application utilises a GET method to get the temperature from the public api but can only access this information with access to a private key.
      
The code from mydb establishes a connection to the rds db through mysql which allows the user to post into the relevant tables found in rds. Once we have established the connection, one can use SQL to query how to access posts and replies. One table is a topic table that includes the subject of the topic and the other table is a reply that needs to be linked with topic through use of the topic id as a primary key in the topic table and a foreign key in this reply table. One first gets the topics and orders them by topic id.

There are two commands within the page in regards to topic. The first command allows one can post a new topic which allows one to create a new topic form (see def new_topic) where one can define the subject and content. This utlises an SQL INSERT command to insert the topic subject and content into the topic table which is automatically assigned a topic_id. The topic_id is a dynamic variable which depends on the most recent topic posted.

The second command allows one to view recently posted topics (see def_view topic) which allows one to implement an SQL select query to select teh relevant topic based on the topi_id being equivalent to the topic selected.
def query_db allows one to run a select query on the database and store values as a key value pair when the key is the column name and the value is the actual value of that column.

RDS allows one to have multiple databases and for this project, I created the database using the MYSQL Engine as well as the Free tier. This specific database allows information to only be accessed by the EC2 instance that i have run as well as the default port 0.0.0.0/0.

Fulfilling requirements for implementing a database schema. For the topics table, one utilises a select method to abstract the topic id and subject in question. One advantage of this dictionary is that one can access the values by simply giving the name of the columns rather than hard coded values i.e. [0],[1].

Within the login method, it firsts the checks the posted username against usernames and passwords within the database login. If the usernames match the database, the database login sends the relevant password and hashkey associated with the username to the SQL server. To check if the password entered by the user and the password accessed from the database match, the application utilising a hash based authentication. The advantage of hash functions that they cannot be decrypted even if the hacker has the hash key or has access to the database, as the hacker will not be able to access the users password, meaning that they are very secure. For hash based authentication, the application will take the password that the user has inputed and the hashkey abstracted from the database, and encrypt them. If the encryption matches what is found in the original database, then the user will be let into the page.

