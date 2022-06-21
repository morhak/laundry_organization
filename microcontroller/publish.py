import json
import time
import os
from machine import Pin

import read_2
import rgb_led
import mqtt
import wifi
from machine import RTC

# This template assumes the following file setup
# - main.py
# - wifi.py
# - mqtt.py
# - cert
#    | - cert.der
#    | - private.der
#    | - wifi_passwds.txt




def convert_to_iso(datetime):
    y, m, d, _, h, mi, s, _ = datetime
    return "{}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(y, m, d, h, mi, s)



def publish_environment_data(mqtt_client, data, iso_timestamp, MQTT_TOPIC):
    rgb_led.greenPin.off()
    rgb_led.redPin.on()
    D_Acht = Pin(15, Pin.IN)
    if D_Acht.value() == True:
        laundry_hamper = "downstairs"
    else:
        laundry_hamper = "upstairs"
    message = {"uid": data, "timestamp": iso_timestamp, "laundry_hamper": laundry_hamper}
    mqtt_client.publish(MQTT_TOPIC, json.dumps(message))
    time.sleep(2)
    rgb_led.redPin.off()
    rgb_led.greenPin.on()


def connect_and_publish():
    print("connect wifi and synchronize RTC")
    wifi.connect()
    wifi.synchronize_rtc()

    print("connect mqtt")
    mqtt_client = mqtt.connect_mqtt()

    print("start publishing data")

    print("")
    print("Place card before reader to read from address 0x08")
    print("")

    rgb_led.greenPin.on()

    while True:
        try :
            timeout = time.time() + 60
            while True:
                data = read_2.do_read()
                if data is not None:
                    MQTT_TOPIC = "rfid"
                    iso_timestamp = convert_to_iso(RTC().datetime())
                    publish_environment_data(mqtt_client, data, iso_timestamp, MQTT_TOPIC)
                    #print("uid", data)
                    break
                elif time.time() > timeout:
                    MQTT_TOPIC = "helper"
                    iso_timestamp = convert_to_iso(RTC().datetime())
                    publish_environment_data(mqtt_client, data, iso_timestamp, MQTT_TOPIC)
                    print("uid", data)
                    break
        except Exception as e:
            print(str(e))
