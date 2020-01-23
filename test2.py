import requests
import datetime
import RPi.GPIO as g
import spidev, time
import Adafruit_DHT

URL = 'http://c9b26d89.ngrok.io/api/sensers'

sensor = Adafruit_DHT.DHT11
dht_pin=2
obstacle=3

g.setmode(g.BCM)
g.setup(obstacle, g.IN)



spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1000000

def analog_read(channel):
    r = spi.xfer2([1, (0x08+channel)<<4, 0])
    adc_out = ((r[1]&0x03)<<8) + r[2]
    return adc_out

while True:
    try:
        while True :
            temp,humi,adc0,adc1,adc2 = 0,0,0,0,0
            for i in range(0,10):
                h, t = Adafruit_DHT.read_retry(sensor, dht_pin)
                temp = temp + t
                humi = humi + h
                adc0 = adc0 + analog_read(0)
                adc1 = adc1 + analog_read(1)
                adc2 = adc2 + analog_read(2)

            if h is not None and t is not None :
                print("Temp = %.2f Humi = %.2f" % (temp/10, humi/10))
                print("ADC0 = %d" % (adc0/10))
                print("ADC1 = %d" % (adc1/10))
                print("ADC2 = %d" % (adc2/10))
                print("obsracle = %d" % (1^g.input(obstacle)))

                now = datetime.datetime.now()
                data = {'humi' : (humi/10), 'temp' : (temp/10), 'gas' : (adc0/10(),
                        'fire' : (adc1/10), 'power' : (adc2/10), 'obsracle' : (1^g.input(obstacle)),
                        'time' : now} 
            else :
                print('Read error')
                time.sleep(1)
            #time.sleep(0.5)
            

    except KeyboardInterrupt:
        print("Terminated by Keyboard")
        exit()


res = requests.post(URL, data=data)
print(res.status_code) 
print(res.text)
