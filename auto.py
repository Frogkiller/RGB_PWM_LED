import time
import math

import Adafruit_PCA9685
import OPi.GPIO as GPIO

GPIO.setmode(GPIO.SUNXI)
GPIO.setup("PA00", GPIO.IN, pull_up_down=GPIO.PUD_OFF)

class Led:
    def __init__(self):
        self.r = 0
        self.g = 0
        self.b = 0
        self.target = [80,0,100]
        self.pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=0)
    
    def set_rgb_raw(self,red,green,blue):
        self.pwm.set_pwm(0,0,red)
        self.pwm.set_pwm(4,0,blue)
        self.pwm.set_pwm(8,0,green)

    def set_rgb(self,red,green,blue):
        self.r = red
        self.g = green
        self.b = blue
        red=self.cor(red)
        green=self.cor(green)
        blue=self.cor(blue)
        self.set_rgb_raw(red,green,blue)

    def off(self):
        self.set_rgb(0,0,0)

    def light_on(self):
        delta_r = (self.target[0]-self.r)/100
        delta_g = (self.target[1]-self.g)/100
        delta_b = (self.target[2]-self.b)/100
        while self.r!= self.target[0] or self.g != self.target[1] or self.b != self.target[2]: 
            time.sleep(0.01)
            self.set_rgb(min(self.r+delta_r,self.target[0]),min(self.g+delta_g,self.target[1]),min(self.b+delta_b,self.target[2]))
            print(delta_r,delta_g,delta_b,min(self.r+delta_r,self.target[0]),min(self.g+delta_g,self.target[1]),min(self.b+delta_b,self.target[2]))

    def light_off(self):
        delta_r = self.r/100
        delta_g = self.g/100
        delta_b = self.b/100
        while self.r!= 0 or self.g!=0 or self.b!=0:
            time.sleep(0.05)
            self.set_rgb(max(self.r-delta_r,0),max(0,self.g - delta_g),max(0,self.b - delta_b))

    def cor(self, x):
        gamma=2.8
        max_in=255
        max_out=4095
        value=int((x/max_in)**gamma*max_out+0.5)
        return value

    def autoloop(self):
        self.pwm.set_pwm_freq(1000)
        pin_state = 0
        while True:
            time.sleep(0.1)
            if GPIO.input("PA00") and pin_state==0:
                pin_state = 1
                self.light_on()
            if GPIO.input("PA00")==0 and pin_state==1:
                pin_state = 0
                self.light_off()


def main():
    loop = Led()
    loop.autoloop()

main()
