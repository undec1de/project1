import subprocess
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Button,Entry,Radiobutton,Checkbutton
from time import sleep
import os
import recordFile, Webcam
import webbrowser
from cmdGen import cmdGen
from sr_settings import settingsWin

class App(Tk): # основной класс для главного окна
    def __init__(self):
        Tk.__init__(self)

        # свойства окна
        self.title(string = "Screen Recorder")
        self.iconbitmap("icon.ico")
        self.resizable(width = False, height = False)

        ffmpegAvailable = False
        for item in os.listdir():
            if item == "ffmpeg.exe":
                ffmpegAvailable = True
                break
        if not ffmpegAvailable:
            self.withdraw()
            if messagebox.askyesno("FFmpeg Not Found","ffmpeg.exe could not be found in screen recorder's directory. Do you want to be redirected to the ffmpeg download website?"):
                webbrowser.open_new_tab("https://ffmpeg.zeranoe.com/builds/")
            exit()
        self.cmdGen = cmdGen()  # создать объект генератора команд для хранения настроек 

        # имя файла
        label1 = Label(self, text="File Name:")
        label1.grid(row = 0, column = 0, sticky = "")
        self.entry1 = Entry(self)
        self.entry1.grid(row = 0, column = 1,sticky="ew")

        # убедитесь в наличии каталога "ScreenCaptures"
        try:
            os.mkdir("ScreenCaptures")
        except FileExistsError:
            pass
        os.chdir("ScreenCaptures")

        # найти имя файла по умолчанию, которое в настоящее время доступно.
        defaultFile = "ScreenCapture.mp4"
        available = False
        fileNum = 0
        while available == False:
            hasMatch = False
            for item in os.listdir():
                if item == defaultFile:
                    hasMatch = True
                    break
            if not hasMatch:
                available = True
            else:
                fileNum += 1
                defaultFile = "ScreenCapture"+str(fileNum)+".mp4"
        os.chdir("..")
        self.entry1.insert(END,defaultFile)

        # радиокнопки определяют, что записывать
        self.what = StringVar()
        self.what.set("desktop")
        self.radio2 = Radiobutton(self, text="record the window with the title of: ", variable=self.what, value = "title", command = self.enDis1)
        self.radio1 = Radiobutton(self, text="record the entire desktop", variable=self.what, value = "desktop", command = self.enDis)
        self.radio1.grid(row = 1, column = 0, sticky="w")
        self.radio2.grid(row = 2, column = 0, sticky = "w")
        self.entry2 = Entry(self, state=DISABLED)
        self.entry2.grid(row = 2, column = 1,sticky="ew")

        # инициализировать веб-камеру
        self.webcamdevices = Webcam.listCam()
        self.webcamrecorder = Webcam.capturer("")
        
        # checkbox "запись с веб-камеры"
        self.rcchecked = IntVar()
        self.recordcam = Checkbutton(self, text="Record from webcam", command = self.checkboxChanged,variable=self.rcchecked)
        self.recordcam.grid(row = 3, column = 0)

        # раскрывающийся список, позволяющий выбрать устройство веб-камеры из доступных устройств захвата DirectShow.
        self.devicename = StringVar(self)
        if self.webcamdevices:
            self.devicename.set(self.webcamdevices[0])
            self.deviceselector = OptionMenu(self, self.devicename, *self.webcamdevices)
            self.deviceselector.config(state=DISABLED)
            self.deviceselector.grid(row = 3, column = 1)
        else:
            self.devicename.set("NO DEVICES AVAILABLE")
            self.recordcam.config(state=DISABLED)
            self.deviceselector = OptionMenu(self, self.devicename, "NO DEVICES AVAILABLE")
            self.deviceselector.config(state=DISABLED)
            self.deviceselector.grid(row = 3, column = 1)
        
        self.opButton = Button(self, text="⚙ Additional Options...",command = self.openSettings)
        self.opButton.grid(row = 4, column=1, sticky='e')

        # кнопка "начать запись"
        self.startButton = Button(self, text="⏺ Start recording", command = self.startRecord)
        self.startButton.grid(row = 5, column = 0, columnspan = 2)


        # некоторые переменные
        self.recording = False      # мы записываем?
        self.proc = None            # объект popen для ffmpeg (во время записи экрана)
        self.recorder = recordFile.recorder()   # объект "рекордер" для аудио (см. recordFile.py)
        self.mergeProcess = None    # объект popen для ffmpeg (при объединении видео и аудио файлов)

        # запустить обратный вызов мониторинга ffmpeg
        self.pollClosed()

    def openSettings(self):
        self.settings = settingsWin(self,self.cmdGen,self.recorder)

    def pollClosed(self):
        
        if self.recording:
            if self.proc.poll() != None:
                self.startRecord()
                messagebox.showerror("ffmpeg error","ffmpeg has stopped working. ERROR: \n"+str(self.proc.stderr.read()).replace('\\r\\n','\n'))
            if self.recorder.error:
                self.startRecord()
        if self.mergeProcess and self.recording == False:
            if self.mergeProcess.poll() != None:
                self.startButton.config(text="⏺ Start Recording", state = NORMAL)
                self.title(string = "Screen Recorder")
        self.after(100, self.pollClosed)

    def enDis(self):
        
        self.entry2.config(state=DISABLED)
        

    def enDis1(self):
        
        self.entry2.config(state = NORMAL)
        

    def checkboxChanged(self):
        
        
        if self.rcchecked.get():
            self.deviceselector.config(state = NORMAL)
        else:
            self.deviceselector.config(state = DISABLED)

    def startRecord(self):
        
        if self.recording == False:
            # изменить окно
            self.title(string = "Screen Recorder (Recording...)")
            self.startButton.config(text="⏹️ Stop Recording")
            self.filename = self.entry1.get()

            # отключить интерфейс
            self.entry1.config(state = DISABLED)
            self.radio1.config(state = DISABLED)
            self.radio2.config(state = DISABLED)
            self.deviceselector.config(state = DISABLED)
            self.opButton.config(state = DISABLED)
            if self.what.get() == "title":
                self.entry2.config(state = DISABLED)

            # обеспечить наличие каталога "tmp"
            try:
                os.mkdir("tmp")
            except FileExistsError:
                pass

            # начать процесс записи экрана
            self.recording = True
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            
            self.cmdGen.setSource(self.what.get()=="title",self.entry2.get())
            command = self.cmdGen.getCmd("tmp/tmp.mkv")
            self.proc = subprocess.Popen(args=command, startupinfo=startupinfo)#,stderr=subprocess.PIPE)

            # начать аудиозапись
            self.recorder.record("tmp/tmp.wav")

            # начать запись с веб-камеры, если отмечено
            self.recordcam.config(state = DISABLED)
            if self.rcchecked.get() and self.webcamdevices:
                self.webcamrecorder.setDevice(str(self.devicename.get()))
                self.webcamrecorder.startCapture("tmp/webcamtmp.mkv")
            
            # минимизировать окно, чтобы убрать его с пути записи
            self.iconify()
        elif self.recording == True:
            self.deiconify()
            defaultFile = self.filename

            # повторно включить интерфейс
            self.entry1.config(state = NORMAL)
            self.radio1.config(state = NORMAL)
            self.radio2.config(state = NORMAL)
            self.opButton.config(state = NORMAL)
            if self.webcamdevices:
                self.recordcam.config(state = NORMAL)
                if self.rcchecked.get():
                    self.deviceselector.config(state = NORMAL)
            if self.what.get() == "title":
                self.entry2.config(state = NORMAL)
            
            available = False
            fileNum = 0

            # остановить все процессы записи
            self.recording = False
            self.proc.terminate()
            if self.rcchecked.get() and self.webcamdevices:
                self.webcamrecorder.stopCapture()
            try:
                os.mkdir("ScreenCaptures")
            except FileExistsError:
                pass

            # изменить заголовок окна и текст кнопки, чтобы отразить текущий процесс
            self.title(string = "Screen Recorder (converting...)")
            self.startButton.config(text="converting your previous recording, please wait...", state = DISABLED)
            
            # начать процесс конвертации видео
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            self.cmdGen.config(audList=self.recorder.devices)
            command = self.cmdGen.getCvtCmd("ScreenCaptures/"+self.filename)
            if not self.recorder.error:
                self.mergeProcess = subprocess.Popen(args=command)#,startupinfo=startupinfo)

            
            os.chdir("ScreenCaptures")
            while True:
                matches = 0
                for item in os.listdir():
                    if item == defaultFile:
                        matches += 1
                if matches == 0:
                    self.entry1.delete(0,END)
                    self.entry1.insert(END,defaultFile)
                    break
                else:
                    fileNum += 1
                    file = self.filename.split(".")
                    defaultFile = file[0].rstrip("1234567890")+str(fileNum)+"."+file[1]

            os.chdir("../")

app = App()
app.mainloop()
print("DONE!")
