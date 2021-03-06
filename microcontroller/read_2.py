#This file was supposed to be for testing only

import mfrc522


def do_read():
	rdr = mfrc522.MFRC522(0, 2, 4, 5, 14)

	(stat, tag_type) = rdr.request(rdr.REQIDL)

	if stat == rdr.OK:

		(stat, raw_uid) = rdr.anticoll()

		if stat == rdr.OK:
			# print("New card detected")
			# print("  - tag type: 0x%02x" % tag_type)
			uid = "0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
			print("  - uid	 :", uid)
			# print("")

			if rdr.select_tag(raw_uid) == rdr.OK:

				key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

				if rdr.auth(rdr.AUTHENT1A, 8, key, raw_uid) == rdr.OK:
					# print("Address 8 data: %s" % rdr.read(8))
					rdr.stop_crypto1()
				else:
					print("Authentication error")
					pass
			else:
				print("Failed to select tag")
				pass
			return uid
