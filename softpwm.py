#!/usr/bin/python

import WB_IO.GPIO as GPIO
import time
import sys



import mosquitto
import threading


gpio_pin = 52
mqtt_device_id = 'wb-fan-control'
device_name = 'Fan control'
control_name = 'speed'
freq = 20

delay_high = 0
delay_low = 1

def on_mqtt_message(mosq, obj, msg):
    #~ print "on_mqtt_message, %s %s %s " % (mosq, obj, msg)
    #~ print msg.payload
    try:
        val = int(msg.payload)
    except:
        return

    if val < 0:
        val = 0
    if val > 255:
        val = 255

    duty_cycle = val * 1.0 / 255
    set_delay(freq, duty_cycle)

    client.publish("/devices/%s/controls/%s" % (mqtt_device_id, control_name), str(val), 0, True)

def set_delay(freq, duty_cycle):
    print "set delay", duty_cycle
    global delay_high, delay_low
    delay_high = 1.0 / freq * duty_cycle
    delay_low = 1.0 / freq * ( 1- duty_cycle)



def pwm_loop():
    GPIO.setup(gpio_pin, GPIO.OUT)
    while True:
        if delay_low > 1E-10:
            GPIO.output(gpio_pin, GPIO.LOW)
            time.sleep(delay_low)

        if delay_high > 1E-10:
            GPIO.output(gpio_pin, GPIO.HIGH)
            time.sleep(delay_high)


if __name__ == '__main__':
    pwm_thread = threading.Thread(target=pwm_loop)
    pwm_thread.daemon = True
    pwm_thread.start()

    client = mosquitto.Mosquitto()
    client.connect("127.0.0.1")
    client.publish("/devices/%s/meta/name" % mqtt_device_id, device_name, 0, True)


    client.publish("/devices/%s/controls/%s/meta/type" % (mqtt_device_id, control_name), "range", 0, True)
    client.publish("/devices/%s/controls/%s/meta/min" % (mqtt_device_id, control_name), "0", 0, True)
    client.publish("/devices/%s/controls/%s/meta/max" % (mqtt_device_id, control_name), "255", 0, True)


    client.subscribe("/devices/%s/controls/%s/on" % (mqtt_device_id, control_name))
    client.on_message = on_mqtt_message

    set_delay(freq, 0)


    try:
        while 1:
            rc = client.loop()
            if rc != 0:
                break
    finally:
        GPIO.setup(gpio_pin, GPIO.IN)


