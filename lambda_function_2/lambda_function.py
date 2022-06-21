import pymysql
import wash_cycle
import publish
 
endpoint = 'endpoint'
username = 'username'
password = 'password'
database_name = 'database_name'


 
#Connection
connection = pymysql.connect(host=endpoint, user=username,
	passwd=password, db=database_name)
 
def lambda_handler(event, context):
	test = wash_cycle.test(connection)
	if test[0] >= 1:
		publish.publish(test[1])
