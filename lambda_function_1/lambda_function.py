'''
A detailed and complete documentation may follow at a later date...
-June 21, 2022
'''



# # # Import of all required libraries and classes # # #
import pymysql
import publish
import sql_update
import wash_cycle
import analysis
import json


# # # Details to build up the connection to the mysql-instance # # #
endpoint = 'endpoint'
username = 'username'
password = 'password'


# # # Main function: starts every time the trigger is fired # # #
def lambda_handler(event, context):
	
	# Extracting the data from the mqtt message #
	tag = event['uid']
	timestamp = event['timestamp']
	
	# Adaptation of the transferred time stamp by the microcontroller to the correct time zone # 
	date = sql_update.timestamp_slice(timestamp)[0]
	time = sql_update.timestamp_slice(timestamp)[1]
	timestamp_corrected = "{} {}".format(date, time)
	
	# Adjustment of the passed value to the code #
	if event['laundry_hamper'] == "upstairs":
		location = 1
	elif event['laundry_hamper'] == "downstairs":
		location = 2
	
	# Selection of the use case, either in private or industrial context # 
	with open("industrial_tags.txt") as f:
		if tag in f.read():
			rfid_industrial("aws_rfid_industrial", tag, timestamp_corrected, location)
		else:
			rfid_private("aws_rfid", tag, timestamp_corrected, date, time, location)
	

# # # Subfunction to call all functions for the private context # # #
def rfid_private(database_name, tag, timestamp, date, time, hamper):
	connection = pymysql.connect(host=endpoint, user=username, passwd=password, db=database_name)

	sql_update.log_entry(connection, tag, hamper, timestamp)
	sql_update.update_sql(connection, tag, hamper, date, time)
	
	test = wash_cycle.test(connection)
	
	if test[0] >= 1:
		publish.publish(test[1])


# # # Subfunction to call all functions for the industrial context # # #
def rfid_industrial(database_name, tag, timestamp, location):
	connection = pymysql.connect(host=endpoint, user=username, passwd=password, db=database_name)
	with open("function_tags_industrial.txt") as f:
		data = f.read()
	js = json.loads(data)
	
	if tag in js.keys():
		sql_update.clothes_pickup(connection, timestamp, js[tag])
		analysis.prediction(connection, js[tag])
	else:
		old_status = sql_update.test_direction_industrial(connection, tag)
		sql_update.update_sql_industrial(connection, tag, location, timestamp)
		sql_update.log_entry_industrial(connection, tag, timestamp)
		analysis.analysis_log(connection, tag, 4, timestamp, old_status)
