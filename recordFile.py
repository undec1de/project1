import pyaudio
import wave
import threading
import time
import subprocess
from tkinter import messagebox

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5


class recorder:
    def __init__(self):
        self.going = False      # процесс запущен?
        self.process = None     # хранит ссылку на фоновый поток
        self.filename = ""      # имя файла для записи 
        self.p = pyaudio.PyAudio()
        self.devices = [None]
        self.error = False
    def record(self,filename):
        # завершить процесс, прежде чем начинать новый
        if self.process and self.process.is_alive():
            self.going = False
        self.error = False
        
        # начать поток записи
        self.process = threading.Thread(target=self._record)
        self.process.start()
        self.filename = filename
    def _record(self):
        try:
            # инициализировать pyaudio
            streams = []
            frames = [] # хранит аудиоданные
            for i in range(len(self.devices)):
                streams.append(self.p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK,
                            input_device_index=self.devices[i]))
                frames.append([])

            print("* recording")

            self.going = True   # дать системе знать, что мы работаем
            
            while self.going:   # транслировать аудио в "кадры"
                for i in range(len(self.devices)):
                    data = streams[i].read(CHUNK)
                    frames[i].append(data)

            print("* done recording")

            # остановить запись
            for i in range(len(self.devices)):
                streams[i].stop_stream()
                streams[i].close()

            # записать аудиоданные в файл (tmp / tmp.wav)
            for i in range(len(self.devices)):
                wf = wave.open(self.filename[:self.filename.find(".")]+"_"+str(i)+self.filename[self.filename.find("."):], 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(self.p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames[i]))
                wf.close()
        except Exception as e:
            self.error = True
            messagebox.showerror("AUDIO ERROR","ERROR ENCOUNTERED RECORDING AUDIO: "+str(e))
    def getDeviceCount(self):
        return self.p.get_device_count()
    def getDeviceName(self,deviceID):
        return self.p.get_device_info_by_index(deviceID)["name"]
    def isInputDevice(self,deviceID):
        return int(self.p.get_device_info_by_index(deviceID)["maxInputChannels"]) > 0
    def getAPIName(self,deviceID):
        return self.p.get_host_api_info_by_index(self.p.get_device_info_by_index(deviceID)["hostApi"])["name"]
    def setToDefault(self):
        self.devices = [None]
    def setToDevices(self,devices):
        self.devices = devices
    def stop_recording(self):
        self.going = False
    def destroy(self):
        self.p.terminate()
        
