import time
import random

#party_mode on

import Adafruit_PCA9685
import OPi.GPIO as GPIO

PIN_NAME = "PA01"
GPIO.setmode(GPIO.SUNXI)
GPIO.setup(PIN_NAME, GPIO.IN, pull_up_down=GPIO.PUD_OFF)

class Led:
    def __init__(self):
        self.rgb = [0,0,0]
        self.party = True
        self.target_party = [0,0,0]
        self.delta = [0,0,0]
        self.target = [80,0,100]
        self.pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=0)
    
    def set_rgb_raw(self,red,green,blue):
        self.pwm.set_pwm(0,0,red)
        self.pwm.set_pwm(4,0,blue)
        self.pwm.set_pwm(8,0,green)

    def set_rgb(self,red,green,blue):
        self.rgb = [red, green, blue]
        red=self.cor(red)
        green=self.cor(green)
        blue=self.cor(blue)
        self.set_rgb_raw(red,green,blue)

    def cor(self, x):
        gamma=2.8
        max_in=255
        max_out=4095
        value=int((x/max_in)**gamma*max_out+0.5)
        return value

    def next_value(self, pin_state):
        if self.party == False:
            self.normal_next(pin_state)
        else:
            self.party_next(pin_state)

    def normal_next(self, pin_state):
        if pin_state == 1 and (self.rgb[0]!= self.target[0] or self.rgb[1] != self.target[1] or self.rgb[2] != self.target[2]):
            self.set_rgb(min(self.rgb[0]+self.delta[0],self.target[0]),min(self.rgb[1]+self.delta[1],self.target[1]),min(self.rgb[2]+self.delta[2],self.target[2]))
        elif pin_state == 0 and (self.rgb[0]!= 0 or self.rgb[1]!=0 or self.rgb[2]!=0):
            self.set_rgb(max(0, self.rgb[0] - self.delta[0]),max(0,self.rgb[1] - self.delta[1]),max(0,self.rgb[2] - self.delta[2]))

    def random_target(self):
        self.target_party = [random.randint(10, 255), random.randint(10, 255), random.randint(10, 255)]
        return random.randint(15, 40)
        
    def party_next(self, pin_state):
        if self.target_party == [0,0,0] or (self.rgb[0] == self.target_party[0] and self.rgb[1] == self.target_party[1] and self.rgb[2] == self.target_party[2]):
            timer = self.random_target()
            self.delta = [(self.target_party[0]-self.rgb[0])/timer, (self.target_party[1]-self.rgb[1])/timer, (self.target_party[2]-self.rgb[2])/timer]
        targets = [0,0,0]
        for i, x in enumerate(self.delta):
            if x<0:
                targets[i] = max(self.target_party[i], self.rgb[i] + self.delta[i])
            else:
                targets[i] = min(self.target_party[i], self.rgb[i] + self.delta[i])
        self.set_rgb(*targets)

    def set_deltas(self, pin_state):
        if self.party == False:
            if pin_state == 1:
                self.delta = [self.target[0]/50, self.target[1]/50, self.target[2]/50]
            else: 
                self.delta = [self.rgb[0]/50, self.rgb[1]/50, self.rgb[2]/50]
        else:
            pass
            

    def autoloop(self):
        self.pwm.set_pwm_freq(1000)
        switch_time = time.time()
        state_duration_off = 9999999
        state_duration_on = 9999999
        pin_state = 0 
        while True:
            time.sleep(0.05)
            if GPIO.input(PIN_NAME) and pin_state==0:
                pin_state = 1
                state_duration_off = time.time() - switch_time
                switch_time = time.time()
                print("on", state_duration_off, state_duration_on, switch_time)
                if state_duration_off < 10 and state_duration_on < 10:
                    self.party = True
                    print("party", state_duration_off, state_duration_on)
                self.set_deltas(pin_state)
            if GPIO.input(PIN_NAME)==0 and pin_state==1:
                pin_state = 0
                state_duration_on = time.time() - switch_time
                switch_time = time.time()
                self.party = False
                self.target_party = [0,0,0]
                print("off", state_duration_off, state_duration_on, switch_time)
                self.set_deltas(pin_state)
            self.next_value(pin_state)
            


def main():
    loop = Led()
    loop.autoloop()

main()
