print("first line")
from threading import Thread
from tkinter import Label,Button,Tk
from tkinter import PhotoImage
from time import sleep,time
from numpy import array
import cv2
import queue
from pyautogui import screenshot, size, position
from sounddevice import query_devices,InputStream
from soundfile import SoundFile
from wave import open
from sys import exit
import moviepy.editor as mpe
from pydub import AudioSegment
from os.path import isfile,isdir
from os import remove,mkdir

if not isdir("Recorded Videos"):
    mkdir("Recorded Videos")

screen_resolution_x = size().width   
screen_resolution_y = size().height  

window = Tk()
window.geometry("700x390")
window["bg"] = "#333B48"
window.resizable(width= "False", height= "False")
window.title("Screen Recorder")

stop = False
start = False
fps = 60 
count1 = 0

# this lebel is for showing processing
m1 = Label(window,text = "" , bg = "#333B48", fg= "red" ,font = ("arial",22,"bold"))
m1.place(x= "200", y= "300")

def generate_new_file_name():
    file_counter = 0
    file_counter_str = ""

    while isfile("Recorded Videos/"+"recorded"+file_counter_str + ".avi") or \
            isfile("Recorded Videos/"+"audio"+file_counter_str+".avi") or \
            isfile("Recorded Videos/"+"video" +file_counter_str+".avi") or \
            isfile("Recorded Videos/"+"recorded"+file_counter_str+".mp4") or \
            isfile("Recorded Videos/"+"audio"+file_counter_str+".mp4") or \
            isfile("Recorded Videos/"+"video" +file_counter_str+".mp4") or \
            isfile("Recorded Videos/"+"recorded "+file_counter_str+".wav") or \
            isfile("Recorded Videos/"+"audio"+file_counter_str+".wav") or \
            isfile("Recorded Videos/"+"video" + file_counter_str+".wav") or \
            isfile("Recorded Videos/"+"recorded "+file_counter_str+".mp3") or \
            isfile("Recorded Videos/"+"audio"+file_counter_str+".mp3") or \
            isfile("Recorded Videos/"+"video" + file_counter_str+".mp3") or \
            isfile("Recorded Videos/"+"frame_checker" + file_counter_str + ".avi"):
        file_counter += 1
        if file_counter != 0:
            file_counter_str = str(file_counter)

    final_file_name = "recorded" + file_counter_str
    temp_video = "video" + file_counter_str
    temp_audio = "audio" + file_counter_str
    frame_checker = "Проверка кадров" + file_counter_str

    return final_file_name, temp_video, temp_audio,frame_checker

def processing_condition_showing(condition):
    print("Условие обработки, показывающее функцию, называется")
    if condition == "Обработка":
        print("Обработка")
        m1.config(text = "Обработка... ", bg = "#333B48", fg = "white")
        m1.place(x = "240", y = "300")
    else:
        m1.config(text = "Готово", bg = "#333B48", fg="white")
        m1.place(x = "280", y = "300")
        
def changing_fps(fps_real, temp_video_file):
    print("НАЧАЛО СМЕНЫ КАДРОВ")
    if(fps_real <6):
        fps_real =6
    fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
    try:
        out = cv2.VideoWriter("Recorded Videos/"+temp_video_file+"_corrected.avi", fourcc, fps_real,(screen_resolution_x, screen_resolution_y))  
    except:
        print("Ошибка произошла в объекте changing_fps")
    try:
        cap = cv2.VideoCapture("Recorded Videos/"+temp_video_file+".avi") 
    except:
        print("Ошибка произошла в видеозаписи changing_fps")
    t = time()
    while cap.isOpened():
        ret, frame = cap.read()
        if ret == True:
	        out.write(frame)
        else:
	        break
    out.release()
    cv2.destroyAllWindows()
    print("СМЕНА КАДРОВ ЗАКОНЧЕНА")
    print("Время, затраченное на изменение кадров в секунду ", time()-t)
	
def audio_recorder(final_file_name, temp_video_file, temp_audio_file):

    q = queue.Queue()
    def callback(indata, frames, time, status):
        q.put(indata.copy())
    device_info = query_devices(0, 'input')
    samplerate = int(device_info['default_samplerate'])
    initial_time = time()
    with SoundFile("Recorded Videos/"+temp_audio_file + ".wav", mode='x', samplerate=samplerate, channels=2) as file:
        with InputStream(samplerate=samplerate, device=0,
                            channels=2, callback=callback):
            while not stop:
                file.write(q.get())

    print("счет1 ",count1)
    print("time()-initial_time = ", time()-initial_time)
    fps_real = count1/(time()-initial_time)	
    processing_condition_showing("Обработка")
    print("Действительный fps ", fps_real)

    changing_fps(fps_real, temp_video_file)

    #merging
    sound = AudioSegment.from_wav("Recorded Videos/"+temp_audio_file + ".wav")
    sound.export("Recorded Videos/"+temp_audio_file + ".mp3")

    clip = mpe.VideoFileClip("Recorded Videos/"+temp_video_file + "_corrected.avi")
    audio = mpe.AudioFileClip("Recorded Videos/"+temp_audio_file + ".mp3")

    final_audio = mpe.CompositeAudioClip([audio])
    final_file = clip.set_audio(final_audio)

    final_file.write_videofile("Recorded Videos/"+final_file_name + ".mp4")

    print("Удаление временных файлов")
    if isfile("Recorded Videos/"+temp_audio_file + ".mp3"):
        remove("Recorded Videos/"+temp_audio_file + ".mp3")
    if isfile("Recorded Videos/"+temp_audio_file + ".wav"):
        remove("Recorded Videos/"+temp_audio_file + ".wav")
    if isfile("Recorded Videos/"+temp_video_file + ".avi"):
        remove("Recorded Videos/"+temp_video_file + ".avi")
        
    if isfile("Recorded Videos/"+temp_video_file + "_corrected.avi"):
        remove("Recorded Videos/"+temp_video_file + "_corrected.avi")
    processing_condition_showing("done")


def recorder_1(out):
    global stop, start, count1, error
    count1 = 0
    print("recorder_1 начатый")

    x_mouse_cordinate = [0, 17, 9, 14, 9, 5, 0, 0]
    y_mouse_cordinate = [0, 17, 16, 25, 27, 18, 24, 0]

    record_started_time = time()
    while not stop:
        fps_time = time()
        count1 += 1
        # sleep(0.2)
        img = screenshot()
        frame = array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pos_x , pos_y = position()

        actual_x_cordinates = [int((screen_resolution_x/1920)*cordinate+pos_x) for cordinate in x_mouse_cordinate]
        actual_y_cordinates = [int((screen_resolution_x/1920)*cordinate+pos_y) for cordinate in y_mouse_cordinate]
        point_cordinates = list(zip(actual_x_cordinates,actual_y_cordinates))
        points = array(point_cordinates, 'int32')
        cv2.fillPoly(frame, [points], color=[0,0,255])
        out.write(frame)

    out.release()
    cv2.destroyAllWindows()
    print("счет1    ",count1)
    print("фактическое зарегистрированное время ", time() - record_started_time)
    print("получение fps " , count1/(time() - record_started_time))
    


time_label = Label(window, text = "Нажмите кнопку ЗАПИСЬ, чтобы начать", pady = 25, padx = 70,fg = "white", bg = "#333B48", font = ("arial",18,"normal"));
time_label.place ( y = "80", )

def timer():
    print("Таймер работает")
    timer_count = 2
    while timer_count>=0:
        time_label.config(text = timer_count,pady = 0, padx = 330,  font = ("arial",50,"normal"))
        timer_count -= 1
        sleep(1)
    time_label.config(text="Запись...", pady = 5, padx = 265, font=("arial", 30, "normal"))

def starting_utility():

    final_file_name, temp_video_file, temp_audio_file, file_counter_str = generate_new_file_name()
    fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')

    sleep(3)
    print("default fps", fps)
    out = cv2.VideoWriter("Recorded Videos/"+temp_video_file + ".avi", fourcc, fps,
                          (screen_resolution_x, screen_resolution_y))  # frame 10.5 at two thread

    t = Thread(target=recorder_1, args=(out,)).start()

    # audio recording
    audio_T = Thread(target=audio_recorder, args=(final_file_name, temp_video_file, temp_audio_file)).start()

def start_recording():
    final_file_name, temp_video_file, temp_audio_file, file_counter_str = generate_new_file_name()
    print(generate_new_file_name())
    global stop, start

    if start:
        print("Уже записываю")
        return
    start = True

    Thread(target = timer).start()
    Thread(target = starting_utility).start()

def stop_recording():
    global stop, start,count1
    stop = True
    start = False
    sleep(0.20)
    time_label.config(text = "Нажмите кнопку ЗАПИСЬ, чтобы начать", pady = 25, padx = 70, fg = "white", font = ("arial", 18, "normal"))
    b2.configure(bg = "#333B48", activebackground = "#333B48")
    stop = False
    print("Запись остановлена")

def close_window():
    print("Закрытие окна")
    stop_recording()
    exit()

m = Label(window, text = "Screen Recorder" ,fg= "red" ,bg= "#25282e", width= 400 ,font = ("arial",22,"bold"))
m.pack(fill = "x", side= "top")


our_button = PhotoImage(file="record.png")
b1 = Button(image=our_button, bg = "#333B48", highlightthickness=0, bd=0, command= start_recording)
b1.place(x = "180", y = "200")

our_button2 = PhotoImage(file="stop.png")
b2 = Button(image=our_button2, bg= "#333B48", highlightthickness=0, bd=0, command= stop_recording)
b2.place(x = "440", y = "200")

our_button3 = PhotoImage(file="exit.png")
b2 = Button(image=our_button3, bg= "#333B48", highlightthickness=0, bd=0, command= close_window)
b2.pack(side = "bottom", anchor = "se",pady = "10",padx= "10")

print("main loopstarted")
window.mainloop()
