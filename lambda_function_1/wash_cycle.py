Waschprogramme = [1, 2, 3, 4, 5, 6, 7]

washable_clothes = ()
df_clothes = []

def clear_tuple():
    global washable_clothes
    liste = list(washable_clothes)
    liste.clear()
    washable_clothes = tuple(liste)


def test_washing_cycle(program, connection):
    cursor = connection.cursor()
    cursor.execute("select count(rfid_tags.tag_uid) from rfid_tags, clothes where washable = True and rfid_tags.tag_uid = clothes.tag_uid and clothes.ideal_program = '{}'".format(program))
    rows = cursor.fetchone()
    if rows[0] >= 3:
        cursor.execute("select clothes.clothing_type, clothes.color, clothes.brand, program.program_name, laundry_hamper.hamper_name, owner.given_name, owner.surname from rfid_tags, clothes, owner, program, laundry_hamper where washable = True and rfid_tags.tag_uid = clothes.tag_uid and clothes.ideal_program = '{}' and clothes.owner_ID = owner.owner_ID and clothes.ideal_program = program.program_ID and rfid_tags.hamper_ID = laundry_hamper.hamper_ID".format(program))
        clothes2wash = cursor.fetchall()
        global washable_clothes
        washable_clothes = washable_clothes + clothes2wash
        return True



def test(connection):
    publish_message = 0
    for programs in Waschprogramme:
        if test_washing_cycle(programs, connection) == True:
            publish_message =+ 1
    
    #msg_clothes ='{} ({}, {}, {})\n'.format("Beschreibung", "Waschprogramm", "Name", "Wäschekorb" )
    msg_clothes = ''
    
    for clothes in washable_clothes:
        a = str("{} {} by {} ({}, {} {}, {})\n".format(clothes[1], clothes [0], clothes[2], clothes [3], clothes[5], clothes[6], clothes[4]))
        msg_clothes = msg_clothes + a

    

    msg = ('''
Hallo Britta,
mittlerweile haben sich riesige Klamottenberge angesammelt...
    
Kannst du daher bitte folgende Klamotten (Waschprogramm, Besitzer, Wäschekorb) mit den entsprechenden Programmen waschen?
    
{}
    
Vielen Dank
Olaf'''.format(msg_clothes))
    
    clear_tuple()
    
    return publish_message, msg
