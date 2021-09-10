 #!/usr/bin/python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

#define pins with BOARD layout
tempHumidPin = 12
rotClockPin = 29        #blue
rotDataPin = 31         #white
rotSwitchPin = 33       #yellow
irSensorPin = 16
ldrPin = 7
ledPin = 11
buzzerPin = 13

#tracking for temp/humidity sensor
cycles = 0
accuracy = 0

#tracking for wind direction
angle = 0
compassDir = 'North'

#input pins
GPIO.setup(irSensorPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#tracking for wind speed
current = GPIO.input(irSensorPin)
previous = current

def setup():
        print("START")
        print("\n___WEATHER SYSTEM___")
        print("Developed by Tim James")
        print("\nPress 'Ctrl+C' to stop")

        #output pins
        GPIO.setup(ledPin, GPIO.OUT)
        GPIO.output(ledPin, GPIO.HIGH)
        GPIO.setup(buzzerPin, GPIO.OUT)
        GPIO.output(buzzerPin, GPIO.LOW)        

        #start IR tracking
        current = GPIO.input(irSensorPin)
        previous = current
        
        #start rotary encoder
        ky040 = KY040(rotClockPin, rotDataPin, rotSwitchPin, rotaryChange, switchPressed)
        ky040.start()
        
def getTempHumidity(pin):        
        global cycles
        global accuracy
        j = 0
        data = []
        i = 0
        j = 0
        tmp = 0
        channel = pin

        time.sleep(1)
        
        GPIO.setup(channel, GPIO.OUT)

        GPIO.output(channel, GPIO.LOW)
        time.sleep(0.02)
        GPIO.output(channel, GPIO.HIGH)

        GPIO.setup(channel, GPIO.IN)
        
        while GPIO.input(channel) == GPIO.LOW:
                continue

        while GPIO.input(channel) == GPIO.HIGH:
                continue

        while j < 40:
                k = 0
                while GPIO.input(channel) == GPIO.LOW:
                        continue

                while GPIO.input(channel) == GPIO.HIGH:
                        k += 1
                        if k > 100:
                                break

                if k < 8:
                        data.append(0)
                else:
                        data.append(1)

                j += 1
                       
        humidity_bit = data[0:8]
        humidity_point_bit = data[8:16]
        temperature_bit = data[16:24]
        temperature_point_bit = data[24:32]
        check_bit = data[32:40]

        humidity = 0
        humidity_point = 0
        temperature = 0
        temperature_point = 0
        check = 0
        tempFahrenheit = 0

        for i in range(8):
                humidity += humidity_bit[i] * 2 ** (7 - i)
                humidity_point += humidity_point_bit[i] * 2 ** (7 - i)
                temperature += temperature_bit[i] * 2 ** (7 - i)
                temperature_point += temperature_point_bit[i] * 2 ** (7 - i)
                check += check_bit[i] * 2 ** (7 - i)

        tmp = humidity + humidity_point + temperature + temperature_point
        tempFahrenheit = temperature * 1.8 + 32

        print("\n__TEMP/HUMIDITY__")
        
        if check == tmp:
                print ("Temp: {", temperature, "degC,", round(tempFahrenheit, 2), "fah }, Humidity: {" , humidity, "%} ")
                accuracy = accuracy + 1
        else:
                if (humidity >= 101 or temperature >= 100):
                        print ("Major Inacuracy Detected")
                        print ("!!Temp: {", temperature, "degC,", round(tempFahrenheit, 2), "fah }, !!Humidity: {" , humidity, "% }")

                else:
                        print ("Minor Inacuracy Detected")
                        print ("!Temp: {", temperature, "degC,", round(tempFahrenheit, 2), "fah }, !Humidity: {" , humidity, "% }")

        cycles = cycles + 1
        if (cycles > 1):
                accuracy_percent = round((accuracy/cycles)*100, 2)
                print ("Accuracy: {", accuracy_percent, "% }")
                
        

class KY040:
    
    CLOCKWISE = 0
    ANTICLOCKWISE = 1

    def __init__(self, clockPin, dataPin, switchPin, rotaryCallback, switchCallback):
        #persist values
        self.clockPin = clockPin
        self.dataPin = dataPin
        self.switchPin = switchPin
        self.rotaryCallback = rotaryCallback
        self.switchCallback = switchCallback

        #setup pins
        GPIO.setup(clockPin, GPIO.IN)
        GPIO.setup(dataPin, GPIO.IN)
        GPIO.setup(switchPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def start(self):
        GPIO.add_event_detect(self.clockPin, GPIO.FALLING, callback=self._clockCallback, bouncetime=250)
        GPIO.add_event_detect(self.switchPin, GPIO.FALLING, callback=self._switchCallback, bouncetime=300)

    def stop(self):
        GPIO.remove_event_detect(self.clockPin)
        GPIO.remove_event_detect(self.switchPin)

    def _clockCallback(self, pin):
        if GPIO.input(self.clockPin) == 0:
            data = GPIO.input(self.dataPin)
            if data == 1:
                self.rotaryCallback(self.ANTICLOCKWISE)
            else:
                self.rotaryCallback(self.CLOCKWISE)

    def _switchCallback(self, pin):
        if GPIO.input(self.switchPin) == 0:
            self.switchCallback()

def rotaryChange(direction):
        global angle
        global compassDir

        if (direction == 1):
            angle += 18

        else:
            angle -= 18

        angle = angle % 360

        if (angle == 0 or angle == 18 or angle == 342):
            compassDir = 'North'
        elif (angle == 36 or angle == 54):
            compassDir = 'NorthEast'
        elif (angle == 72 or angle == 90 or angle == 108):
            compassDir = 'East'
        elif (angle == 126 or angle == 144):
            compassDir = 'SouthEast'
        elif (angle == 162 or angle == 180 or angle == 198):
            compassDir = 'South'
        elif (angle == 216 or angle == 234):
            compassDir = 'SouthWest'
        elif (angle == 252 or angle == 270 or angle == 288):
            compassDir = 'West'
        else:
            compassDir = 'NorthWest'

def switchPressed():
        print ('button pressed')
                    
def getWindDirection():
        print("\n__WIND-DIRECTION__")
        print ("Angle: {", str(angle), "' }")
        print ("Compass: {", compassDir, "}")

def getWindSpeed():
        global previous
        global current
        speed = 0
        tempCycles = 0
        
        print("\n__WIND-SPEED__")      
        while (tempCycles < 100):
            current = GPIO.input(irSensorPin) 
            if current != previous:
                speed += 1
            tempCycles += 1
            time.sleep(0.01)
            previous = current
                    
        print ("Speed: {", speed, " rotations/second}")

def timer(pin2):
        reading = 0
        GPIO.setup(pin2, GPIO.OUT)
        GPIO.output(pin2, GPIO.LOW)
        time.sleep(0.2)
        GPIO.setup(pin2, GPIO.IN)
        while (GPIO.input(pin2) == GPIO.LOW):
                reading += 1
        return reading

def getLightLevel():
        result = timer(ldrPin) * 12
        if (result > 100):
                result = 100
        result = 100 - result
        
        print("\n__LIGHT-INTENSITY__")
        print ("Intensity: {", result, "% }")

def led1(state):
        if (state == 'on'):
                GPIO.output(ledPin, GPIO.HIGH)
        else:
                GPIO.output(ledPin, GPIO.LOW)

def buzzer(state):
        if (state == 'on'):
                GPIO.output(buzzerPin, GPIO.HIGH)
        else:
                GPIO.output(buzzerPin, GPIO.LOW)

def loop():     #main loop
        GPIO.setmode(GPIO.BOARD)
        while True:
                time.sleep(1)
                print("\n...")
                getTempHumidity(tempHumidPin)
                getWindDirection()
                getWindSpeed()
                getLightLevel()
                
def destroy():
        print("\nEND")
        GPIO.output(ledPin, GPIO.HIGH)
        GPIO.output(buzzerPin, GPIO.LOW)
        GPIO.cleanup()  # Release resource
        
if __name__ == '__main__':     # Program start from here
	setup()
	try:
		loop()
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
		destroy()
