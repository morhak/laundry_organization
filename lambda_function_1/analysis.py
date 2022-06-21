import sql_update
import datetime

def analysis_log(connection, tag, status_ID, timestamp, old_status):
    if old_status == 3:
        cursor = connection.cursor()
        cursor.execute("select company.company_ID from rfid_tags, company, owner where rfid_tags.tag_uid = '{}' and rfid_tags.owner_ID = owner.owner_ID and owner.company_ID = company.company_ID".format(tag))
        company_ID = cursor.fetchone()[0]
        cursor.execute("select count(rfid_tags.tag_uid) from rfid_tags, owner where rfid_tags.owner_ID = owner.owner_ID and owner.company_ID = '{}' and rfid_tags.status_ID = 4".format(company_ID))
        quantity = cursor.fetchone()[0]
        cursor.execute("Insert into analysis_log (company_ID, timestamp, quantity) values('{}', '{}', '{}')".format(company_ID, timestamp, quantity))
        connection.commit()
        prediction(connection, company_ID)
        


def prediction(connection, company_ID):
    avg_diff = []
    limit = 10
    cursor = connection.cursor()
    cursor.execute("Select * from analysis_log where company_ID = '{}'".format(company_ID))
    entries = cursor.fetchall()
    
    for i in range(len(entries)):
        if entries[i][3] != 0 and i != 0:
            diff = (entries[i][2] - entries[i-1][2]).total_seconds()
            avg_diff.append(diff)
    
    avg = sum(avg_diff) / len (avg_diff)
    limit_attainment = (entries[-1][2] + datetime.timedelta(seconds = (limit - entries[-1][3]) * avg)).replace(microsecond = 0)
    
    cursor.execute("update prediction set prediction = '{}' where company_ID = '{}'".format(limit_attainment, company_ID))
    connection.commit()
