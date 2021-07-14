#!/usr/bin/env python
# coding: utf-8

import time
from pymeasure.instruments.srs import SR830

class MY_SR830(SR830):
    def __init__(self, GPIB_Addr):
        super(MY_SR830, self).__init__("GPIB::%d" %GPIB_Addr)
        
    def SENSITIVITY_AUTO(self, delay_time, step_ratio=2, bottom_ratio=0.1):
        new_sens = self.sensitivity
        if self.is_out_of_range():
            while self.is_out_of_range():
                new_sens *= step_ratio
                self.sensitivity = new_sens
                time.sleep(delay_time)
        else:
            while self.magnitude/new_sens<bottom_ratio:
                new_sens /= step_ratio
                self.sensitivity = new_sens
                time.sleep(delay_time)
                
    def GOTO(self, final_value, step, delay_time, step_ratio=2, bottom_ratio=0.5):
        if final_value<4e-3:
            raise RuntimeError("Set voltage is not accepted!")
        now_value = self.sine_voltage
        if final_value>now_value:
            while now_value<final_value:
                now_value += step
                target = min(now_value, final_value)
                self.sine_voltage = target
                time.sleep(delay_time)
                #self.SENSITIVITY_AUTO(delay_time, step_ratio, bottom_ratio)
        elif final_value<now_value:
            while now_value>final_value:
                now_value -= step
                target = max(now_value, final_value)
                self.sine_voltage = target
                time.sleep(delay_time)
                #self.SENSITIVITY_AUTO(delay_time, step_ratio, bottom_ratio)

