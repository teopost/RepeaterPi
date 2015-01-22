'''
PeaterPiPyr
COPYRIGHT 2013 ANDY KNITT
License:  Free to use and modify for personal and noncommercial use.  
If you plan to make money using this code, contact the author for licensing options.
'''

import time
import datetime
import subprocess
import pyaudio
import wave
import sys
from iniparse.compat import ConfigParser
import os
import errno
from numpy import zeros, short, fromstring, array
import traceback

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("log.txt", "w")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

# This delay function is used in place of time.sleep() when multiple
# processes are active to prevent one sleep catching from stopping another sleep

def wait_sec(waittime):
	starttime = time.time()
	while (time.time()-starttime < waittime):
		pass

def record(seconds):
	all = []
	#stream.start_stream()
	for i in range(0, int(RATE / chunk * seconds)):
				data = stream.read(chunk)
				all.append(data)
	data = ''.join(all)
	#stream.stop_stream()
	return data

def alert(audiobuffer=''):
		#record audio
		print "rilevato audio... "
		all = []
		all.append(audiobuffer)

		for i in range(0, int(RATE / chunk * record_seconds)):
			filedata = stream.read(chunk)
			all.append(filedata)
		

		quiet_samples=0

		print "attendo il silenzio..."
		while quiet_samples < (release_time*5):	
			temp=[]
			for i in range(0, int(RATE / chunk * .2)):
				filedata = stream.read(chunk)
				temp.append(filedata)
				filedata = ''.join(temp)
			all.append(filedata)
			audio_data  = fromstring(filedata, dtype=short)

			# teo
			print abs(max(audio_data))
			if abs(max(audio_data)) < audio_threshold:
				quiet_samples = quiet_samples+1
			else:
				quiet_samples = 0
		if int(release_time*-5) > 0:
			all = all[:int(release_time*-5)]	
		filedata = ''.join(all)
		#recordstream.close()
		#pr.terminate()

		# write data to WAVE file
		now = str(datetime.datetime.now())
		now = now.replace('.','_')
		now = now.replace(':','_')
		now = now.replace(' ','')
		fname = './audio/temp.wav'
		WAVE_OUTPUT_FILENAME = fname


		#create the /audio directory if it doesn't already exist
		try:
			os.makedirs('./audio')
		except OSError, e:
			if e.errno != errno.EEXIST:
				raise

		wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
		wf.setnchannels(CHANNELS)
		wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
		wf.setframerate(RATE)
		wf.writeframes(filedata)
		wf.close()
		print "file WAV creato " + time.strftime('%H:%M:%S')
			
		#THIS IS WHERE WE WILL ACTIVATE THE TRANSMITTER AND REPLAY THE AUDIO
		subprocess.call(["sudo","python","TX.py"])


		#need to replay the paging tones here somehow, either by recording it or reproducing it
		wf = wave.open(WAVE_OUTPUT_FILENAME, 'rb')
		print "apro il file creato"
		# read data (based on the chunk size)
		playdata = wf.readframes(chunk)
		# play stream (looping from beginning of file to the end)
		print "riproduco registrazione"
		while playdata != '':
			# writing to the stream is what *actually* plays the sound.
			#playstream.write(playdata)	#use this to play through onboard sound
			stream.write(playdata)		#use this to play through USB sound
			playdata = wf.readframes(chunk)
		print "riproduzione completata"
		wf.close()
	
		if os.path.exists('beep.wav'):
			wf = wave.open('beep.wav', 'rb')
			print "opened beep file"
			# read data (based on the chunk size)
			playdata = wf.readframes(chunk)
			# play stream (looping from beginning of file to the end)
			print "eseguo beep"
			while playdata != '':
				# writing to the stream is what *actually* plays the sound.
				#playstream.write(playdata)	#use this to play through onboard sound
				stream.write(playdata)		#use this to play through USB sound
				playdata = wf.readframes(chunk)
		
		#UNKEY THE TRANSMITTER AND SWITCH BACK THE ANTENNA HERE
		subprocess.call(["sudo","python","RX.py"])

		'''
		try:
			os.remove(fname)
		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2,file=sys.stdout)
		'''
		print ""
		return

# -------- MAIN -----------------

if __name__ == '__main__':

   sys.stdout = Logger()

   try:
	p = pyaudio.PyAudio()

	# list of the names of the audio input and output devices
	input_devices = []
	output_devices = []

	# dictionary of the audio input and output devices that corellates the name to the index
	input_device_indices = {}
	output_device_indices = {}

	# FIND THE AUDIO DEVICES ON THE SYSTEM
	info = p.get_host_api_info_by_index(0)
	numdevices = info.get('deviceCount')

	# for each audio device, determine if is an input or an output and add it to the appropriate list and dictionary
	for i in range (0,numdevices):
		if p.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')>0:
			input_devices.append(p.get_device_info_by_host_api_device_index(0,i).get('name'))
			input_device_indices[p.get_device_info_by_host_api_device_index(0,i).get('name')] = i
			inv_input_device_indices = dict((v,k) for k,v in input_device_indices.iteritems())

		if p.get_device_info_by_host_api_device_index(0,i).get('maxOutputChannels')>0:
			output_devices.append(p.get_device_info_by_host_api_device_index(0,i).get('name'))
			output_device_indices[p.get_device_info_by_host_api_device_index(0,i).get('name')] = i
			inv_output_device_indices  = dict((v,k) for k,v in output_device_indices.iteritems())

	p.terminate()
	
   except:
	exc_type, exc_value, exc_traceback = sys.exc_info()
	traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2,file=sys.stdout)

   print "eseguo RX.py"
   subprocess.call(["sudo","python","RX.py"])

   try:
	config = ConfigParser()
	config.read('config.cfg')
	record_seconds = config.getfloat('Section1','record_seconds')
	trigger_time = int(5*config.getfloat('Section1','trigger_time'))
	if trigger_time >7:
		trigger_time = 7
	if trigger_time <=0:
		trigger_time = .2
	release_time = config.getfloat('Section1','release_time')
	input_device = config.getint('Section1','input_device_index')
	output_device = config.getint('Section1','output_device_index')
	audio_threshold = config.getint('Section1','audio_threshold')

	#make sure the audio_threshold value is not zero to avoid math issues
	if audio_threshold < 1:
		audio_threshold = 1


   except:
	exc_type, exc_value, exc_traceback = sys.exc_info()
	traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2,file=sys.stdout)


   try:
	p = pyaudio.PyAudio()
	#chunk =2048
	chunk =1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 1 #chan
	RATE = 11025
	#print time.time()
	stream = p.open(format = FORMAT,
					channels = CHANNELS,
					rate = RATE,
					input = True,
					output = True,
					frames_per_buffer = chunk,
					input_device_index = input_device,
					output_device_index = output_device)
   except:
	exc_type, exc_value, exc_traceback = sys.exc_info()
	traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2,file=sys.stdout)

   #stream.stop_stream()
   #print time.time()

   audiobuffer = ['0']*8*5	#8 second long audio buffer
   precount = 0
   while 1:
	#record 200ms of sound
	#print time.time()
	data = record(.2)
	audiobuffer.append(data)
	audiobuffer.pop(0)
	#audiobuffer = audiobuffer[1:]
	audio_data  = fromstring(data, dtype=short)
	if abs(max(audio_data))>audio_threshold:
		precount = precount + 1
	if precount >= trigger_time:
		precount = 0
		audiobuffer = audiobuffer[(len(audiobuffer)-trigger_time)::]
		print len(audiobuffer)
		prerecord = ''.join(audiobuffer)
		audiobuffer = ['0']*8*5	#reset the 8 second long audio buffer to be empty data
		alert(prerecord)
		stream.stop_stream()
		stream.start_stream()

