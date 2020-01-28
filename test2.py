import requests
import datetime
import RPi.GPIO as g
import spidev, time
import Adafruit_DHT
import threading   

URL = 'http://821e5e43.ngrok.io/api/sensors'

sensor = Adafruit_DHT.DHT11
dht_pin=2
obstacle=3

g.setmode(g.BCM)
g.setup(obstacle, g.IN)

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1000000

sensitivity = 0.2
temp,humi,adc0,adc1,adc2 = 0,0,0,0,0

class AsyncTask:
    def __init__(self):
        pass

    def sensing(self):
        global sensitivity
        global temp
        global humi
        global adc0
        global adc1
        global adc2
        
        def analog_read(channel):
            r = spi.xfer2([1, (0x08+channel)<<4, 0])
            adc_out = ((r[1]&0x03)<<8) + r[2]
            return adc_out

        try:
            h, t = Adafruit_DHT.read_retry(sensor, dht_pin)
            temp = temp*(1-sensitivity) + t*sensitivity
            humi = humi*(1-sensitivity) + h*sensitivity
            adc0 = adc0*(1-sensitivity) + analog_read(0)*sensitivity
            adc1 = adc1*(1-sensitivity) + analog_read(1)*sensitivity
            adc2 = adc2*(1-sensitivity) + analog_read(2)*sensitivity

            if h is not None and t is not None :
                print("Temp = %.2f Humi = %.2f" % (temp, humi))
                print("ADC0 = %.2d" % (adc0))
                print("ADC1 = %.2d" % (adc1))
                print("ADC2 = %.2d" % (adc2))
                print("obsracle = %d" % (1^g.input(obstacle)))
        
            else :
                print('Read error')
                time.sleep(1)
                #time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("Terminated by Keyboard")
            exit()
        threading.Timer(1,self.sensing).start()  

    def post_data(self):
        print ('post_data')
        dt = datetime.datetime.now()
        now = dt.strftime("%Y-%m-%d %H:%M:%S")
        data = {'humi' : round(humi,2), 'temp' : round(temp,2), 'gas' : round(adc0,2),
                'fire' : round(adc1,2), 'power' : round(adc2,2), 'obsracle' : (1^g.input(obstacle)),
                'date' : now} 
        print("%s"%now)
        res = requests.post(URL, data=data)
        print(res.status_code) 
        print(res.text)
        threading.Timer(4, self.post_data).start()



def main():
    print ('Async Function')
    at = AsyncTask()
    at.sensing()
    at.post_data()

if __name__ == '__main__':
    main()

