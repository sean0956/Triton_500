#!/usr/bin/env python
# coding: utf-8

import re, time
import numpy as np
import pyvisa as visa


class MY_KEITHLEY236():
    def __init__(self, GPIB_Addr, SM, compliance, range_m = 0):
        rm = visa.ResourceManager()
        self.machine = rm.open_resource(f'GPIB0::{GPIB_Addr}::INSTR')
        self.compliance = compliance
        if SM!='SIMV' and SM!='SVMI':
            raise RuntimeError("Wrong source-measure mode! Must assign SVMI or SIMV !")
        else:
            self.SM = SM
        self.range_m = range_m
        
    def STRING_TO_VALUE(self, string):
        string = re.sub(r'^[A-Z]*', '', string)
        base, exp = string.split('E', 1)
        base = np.float64 (base)
        exp = np.float64 (re.sub(r'E', '', exp))
        return base*10**exp
    
    def READ_OUT(self, mode, print_out=False):
        if mode=='S':
            self.machine.write("G1,0,0")
        elif mode=='M':
            self.machine.write("G4,0,0")
        self.machine.write("N1X")  # To switch the mode to source/measure certainly
        target = self.machine.read()
        string = target.split(',',1)[0]

        if string[0] != 'N':
            raise RuntimeError('Compliance is exceeded!')
        else:
            if string[1] == 'S':
                if string[4] == 'V':
                    value = self.STRING_TO_VALUE(string)
                    if print_out:
                        print('Source is voltage, value is %.6e V.' %value)

                elif string[4] == 'I':
                    value = self.STRING_TO_VALUE(string)
                    if print_out:
                        print('Source is current, value is %.6e A.' %value)

            elif string[1] == 'M':
                if string[4] == 'V':
                    value = self.STRING_TO_VALUE(string)
                    if print_out:
                        print('Measured is voltage, value is %.6e V.' %value)

                elif string[4] == 'I':
                    value = self.STRING_TO_VALUE(string)
                    if print_out:
                        print('Measured is current, value is %.6e A.' %value)
        return value

    def INITIALIZE(self, SM, compliance, range_m, init_value=0.0):
        #self.machine.write("*RST")
        base, exp = str("%.4e"%compliance).split('e')
        exp = exp[0] + re.sub(r'^0*', '', exp[1:])

        if SM == 'SVMI':
            self.machine.write("F0,0X")
        elif SM == 'SIMV':
            self.machine.write("F1,0X")

        self.machine.write("H0X")
        self.machine.write("B" +str(init_value) +",0,0X")
        self.machine.write("N1X")
        self.machine.write("L"+base+"E"+exp+","+str(range_m)+"X") # L1E-7 means level, 3X means range (), see 236 manual 3.6.10

    def GOTO(self, final_value, step, delay_time, compliance = 0.0, range_m = 0, reset_compliance=False):
        if reset_compliance:
            base, exp = str("%.4e"%compliance).split('e')
            exp = exp[0] + re.sub(r'^0*', '', exp[1:])
            self.machine.write("L"+base+"E"+exp+","+str(range_m)+"X") # L1E-7 means level, 3X means range (), see 236 manual 3.6.10
        else:
            compliance = self.compliance
            range_m = self.range_m
            
        now_value = self.READ_OUT('S')
        if now_value<final_value:
            while now_value<final_value:
                now_value += step
                target = min(now_value, final_value)
                self.machine.write("B" +str("%e"%target) +",0,0X")
                self.READ_OUT('M')  # to check complinace
                #self.machine.write("N1X")
                time.sleep(delay_time)
        elif now_value>final_value:
            while now_value>final_value:
                now_value -= step
                target = max(now_value, final_value)
                self.machine.write("B" +str("%e"%target) +",0,0X")
                self.READ_OUT('M')  # to check complinace
                #self.machine.write("N1X")
                time.sleep(delay_time)

    def OPERATE_OFF(self):
        self.machine.write("N0X")