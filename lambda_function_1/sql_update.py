#already_edited als Schutz vor einem direkten ein- und auslagern, da beim Event keine Richtung angegeben wird. Die Richtung wird logisch auf Basis von Vergangenheitsdaten ermittelt.""

def update_sql(connection, tag, hamper, date, time):
    cursor = connection.cursor()
    update_1 = "Update rfid_tags set washable = true, hamper_ID = '{}', already_edited = true, date = '{}', time = '{}' Where tag_uid = '{}' and already_edited = false and washable = false".format(hamper, date, time, tag)
    update_2 = "Update rfid_tags set washable = false, hamper_ID = 0, already_edited = true, date = '{}', time = '{}' Where tag_uid = '{}'  and already_edited = false and washable = true".format(date, time, tag)
    cursor.execute(update_1)
    connection.commit()
    cursor.execute(update_2)
    connection.commit()
    cursor.execute("update rfid_tags set already_edited = false")
    connection.commit()
    show_table(connection)

def update_sql_industrial(connection, tag, location, timestamp):
    cursor = connection.cursor()
    cursor.execute("Select status_ID from rfid_tags where tag_uid = '{}'".format(tag))
    status = cursor.fetchone()
    if status[0] == 4:
        pass #new_status = 1
    else:
        new_status = status[0] +1
        cursor.execute("Update rfid_tags set status_ID = '{}', location = '{}', timestamp = '{}' where tag_uid = '{}'".format(new_status,location, timestamp, tag))
    connection.commit()
    show_table(connection)


def show_table(connection):
    cursor = connection.cursor()
    cursor.execute("select * from rfid_tags")
    rows = cursor.fetchall()
    for row in rows:
    	print("{0} {1} {2} {3} {4}".format(row[0], row[1], row[2], row[3], row[4]))
    	
def timestamp_slice(timestamp):
	data_timestamp = timestamp.split("T",-1)
	date_false = data_timestamp[0]
	date_ymd = date_false.split("-",-1)
	time_false = data_timestamp[1]
	time_hms = time_false.split(":",-1)
	if int(time_hms[0])<22:
		hour = int(time_hms[0])+2
		day = int(date_ymd[2])
	else:
		hour = int(time_hms[0])-22
		day = int(date_ymd[2]) + 1
	time = "{:02d}:{:02d}:{:02d}".format(hour, int(time_hms[1]), int(time_hms[2]))
	date = "{:04d}-{:02d}-{:02d}".format(int(date_ymd[0]), int(date_ymd[1]), day)
	
	return date, time
	
def test_direction(connection, tag):
    cursor = connection.cursor()
    cursor.execute("select washable from rfid_tags where tag_uid = '{}'".format(tag))
    result = cursor.fetchone()
    if result[0] == 0:
        return "in"
    else:
        return "out"

def test_direction_industrial(connection, tag):
    cursor = connection.cursor()
    cursor.execute("select status_ID from rfid_tags where tag_uid = '{}'".format(tag))
    result = cursor.fetchone()
    return result[0]
    #if result[0] == 3:
    #    return "out"
    #else:
    #    return "in"

def log_entry(connection, tag, hamper_ID, timestamp):
    direction = test_direction(connection, tag)
    cursor = connection.cursor()
    cursor.execute("Insert into reading_log (tag_uid, direction, hamper_ID, timestamp) values('{}', '{}', '{}','{}')".format(tag, direction, hamper_ID, timestamp))
    connection.commit()

def log_entry_industrial(connection, tag, timestamp):
    cursor = connection.cursor()
    cursor.execute("Select status_ID from rfid_tags where tag_uid = '{}'".format(tag))
    new_status_ID = cursor.fetchone()[0]
    cursor.execute("Insert into reading_log (tag_uid, timestamp, new_status_ID) values('{}', '{}', '{}')".format(tag, timestamp, new_status_ID))
    connection.commit()
    
def clothes_pickup(connection, timestamp, company_ID):
    cursor = connection.cursor()
    cursor.execute("Select rfid_tags.tag_uid from rfid_tags, owner, company where owner.company_ID = '{}' and rfid_tags.status_ID = 4 and rfid_tags.owner_ID = owner.owner_ID and owner.company_ID = company.company_ID".format(company_ID))
    affected_tags = cursor.fetchall()
    cursor.execute("Select count(rfid_tags.tag_uid) from rfid_tags, owner, company where owner.company_ID = '{}' and rfid_tags.status_ID = 4 and rfid_tags.owner_ID = owner.owner_ID and owner.company_ID = company.company_ID".format(company_ID))
    quantity = cursor.fetchone()[0]
    if quantity > 0:
        cursor.execute("Update rfid_tags, owner set rfid_tags.status_ID = 1, rfid_tags.timestamp = '{}' where owner.company_ID = '{}' and rfid_tags.status_ID = 4 and rfid_tags.owner_ID = owner.owner_ID".format( timestamp, company_ID))
        connection.commit()
        cursor.execute("Insert into analysis_log (company_ID, timestamp, quantity) values('{}', '{}', '{}')".format(company_ID, timestamp, 0))
        connection.commit()
        for tag in affected_tags:
            log_entry_industrial(connection, tag[0], timestamp)
    show_table(connection)
