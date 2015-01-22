#Embedded file name: LevelMeter.py
import pyaudio
import sys
import os
import errno
import numpy as np
from numpy import zeros, short, fromstring, array
from numpy.fft import fft
import collections
from collections import defaultdict
import re
import traceback
import operator
try:
    p = pyaudio.PyAudio()
    input_devices = []
    output_devices = []
    input_device_indices = {}
    output_device_indices = {}
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    print ' '
    print 'AUDIO DEVICE LISTING:'
    for i in range(0, numdevices):
        if p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
            input_devices.append(p.get_device_info_by_host_api_device_index(0, i).get('name'))
            input_device_indices[p.get_device_info_by_host_api_device_index(0, i).get('name')] = i
            inv_input_device_indices = dict(((v, k) for k, v in input_device_indices.iteritems()))
            print 'Input Device ' + str(i) + ': ' + p.get_device_info_by_host_api_device_index(0, i).get('name')
        if p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels') > 0:
            output_devices.append(p.get_device_info_by_host_api_device_index(0, i).get('name'))
            output_device_indices[p.get_device_info_by_host_api_device_index(0, i).get('name')] = i
            inv_output_device_indices = dict(((v, k) for k, v in output_device_indices.iteritems()))
            print 'Output Device ' + str(i) + ': ' + p.get_device_info_by_host_api_device_index(0, i).get('name')

    p.terminate()
except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

input_device = raw_input('\nEnter input device index: ')
output_device = raw_input('Enter output device index: ')
try:
    p = pyaudio.PyAudio()
    chunk = 2048
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 11025
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=False, frames_per_buffer=chunk, input_device_index=int(input_device), output_device_index=int(output_device))
except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

def record(seconds):
    all = []
    for i in range(0, int(RATE / chunk * seconds)):
        data = stream.read(chunk)
        all.append(data)

    data = ''.join(all)
    return data


while 1:
    data = record(0.2)
    audio_data = fromstring(data, dtype=short)
    print abs(max(audio_data))
