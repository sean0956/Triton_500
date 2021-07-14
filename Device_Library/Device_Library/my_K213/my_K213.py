
# coding: utf-8

import pyvisa as visa
import numpy as np
import re
import time

class MY_KEITHLEY213():
    def __init__(self, GPIB_Addr, port, auto_range=True, range_m=1):
        rm = visa.ResourceManager()
        self.machine = rm.open_resource(f'GPIB0::{GPIB_Addr}::INSTR')
        self.selected_port = "P%d"%port
        print("Port %d is selected."%port)
        if auto_range:
            self.range_m = 'A1'
        else:
            self.range_m = "A0R%d"%range_m
        self.machine.write("%s%sX"%(self.selected_port, self.range_m))
        #print("%s%sX"%(self.selected_port, self.range_m))
        
    def GET_PORT(self):
        self.machine.write("P?X")
        port = self.machine.read() # query the current port
        port = re.sub(r'[\n,\r]','', port)
        return port
    def GET_RANGE(self, port=None):
        if port is None:
            self.machine.write("%sA?X" %self.selected_port)
        else:
            self.machine.write("P%dA?X" %port)
        temp = self.machine.read()
        if 'A1' in temp:
            return 'Auto-range'
        else:
            if port is None:
                self.machine.write("%sR?X" %self.selected_port)
            else:
                self.machine.write("P%dR?X" %port)
            range_m = self.machine.read()
            range_m = re.sub(r'[\n,\r]','', range_m)
            return range_m
    def GET_OUTPUT(self, port=None):
        if port is None:
            self.machine.write("%sV?X" %self.selected_port)
        else:
            self.machine.write("P%dV?X" %port)
        voltage = self.machine.read()
        voltage = re.sub(r'^[\D]*','', voltage)
        voltage = re.sub(r'[\D]*$','', voltage)
        voltage = eval(voltage)
        return voltage
    def GET_STATUS(self, port=None):
        if port is None:
            self.machine.write("%sA?R?V?X" %self.selected_port)
        else:
            self.machine.write("P%dP?A?R?V?X" %port)
        status = self.machine.read()
        if 'A1' in status:
            auto_range = True
        else:
            auto_range = False
            range_m = re.findall(r'R[1-9]', status)
        voltage = re.sub(r'^.*V','', status)
        voltage = re.sub(r'[\D]*$','', voltage)
        voltage = eval(voltage) 
        if auto_range:
            if port is None:
                return '%s is auto-range, output voltage is %.6f .' %(self.selected_port, voltage)
            else:
                return 'P%d is auto-range, output voltage is %.6f .' %(port, voltage)
        else:
            if port is None:
                return '%s has range %s, output voltage is %.6f .' %(self.selected_port, range_m, voltage)
            else:
                 return 'P%d has range %s, output voltage is %.6f .' %(port, range_m, voltage)
    def GOTO(self, final_value, step, delay_time, port, reset_range=False, auto_range = False, range_m=1):
        if reset_range:
            if auto_range:
                self.range_m = 'A1'
            else:
                self.range_m = "A0R%d"%range_m
            self.machine.write("%sX"%self.range_m)
 #       self.machine.write("P%d X"%port)
        now_value = self.GET_OUTPUT(port)
        if final_value>now_value:
            while final_value>now_value:
                now_value = min(now_value+step, final_value)
                self.machine.write("P%d V%.4fX"%(port, now_value))
                time.sleep(delay_time)
                #print(self.GET_OUTPUT())
        elif final_value<now_value:
            while final_value<now_value:
                now_value = max(now_value-step, final_value)
                self.machine.write("P%d V%.4fX"%(port, now_value))
                time.sleep(delay_time)
                #print(self.GET_OUTPUT())
    def ZERO(self, step, delay_time, port=None):
        if port is None:
            port = eval(re.findall(r'[1-9]', self.selected_port)[0])
        self.GOTO(0.0, step, delay_time, port)

