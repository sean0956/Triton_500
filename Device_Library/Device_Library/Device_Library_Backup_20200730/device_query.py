#!/usr/bin/env python
# coding: utf-8

import pyvisa as visa

def GPIB_QUERY():
    rm = visa.ResourceManager()
    print(rm.list_resources())
    return rm
