import openai
import speech_recognition  # распознавание пользовательской речи (Speech-To-Text)
import asyncio
import numpy as np
from scipy.io import wavfile

import sys
import time
import subprocess
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import ST7789
from datetime import datetime
import pyaudio
import matplotlib.pyplot as plt
import os
import os.path
import cv2
from googletrans import Translator
from picamera2 import MappedArray, Picamera2, Preview

import serial, time
import RPi.GPIO as GPIO


ser = serial.Serial ('/dev/ttyAMA1') #Open named port
ser.baudrate = 115200 #Set baud rate to 9600



        



picam2 = Picamera2()
picam2.start_preview(Preview.QTGL)
preview_config = picam2.create_preview_configuration(main={"size": (800, 600)})
picam2.configure(preview_config)
picam2.start()






p01=''


recognizer = speech_recognition.Recognizer()
microphone = speech_recognition.Microphone()
CHUNK = 2048  # size of audio chunk for processing
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100  # sample rate of audio stream
RECORD_SECONDS = 0.5  # number of seconds to record audio for
THRESHOLD = 0.1 # threshold for sound detection
keyword_sound_file = "8df4abb9-e903-4a5f-8586-d3fcfd612d19-byVC.wav"

ActiveFlag=False

def key():
    with open("gpt_code.txt", "r") as f:
        key = f.readlines()[0][:-1]
        print(key)
    return key
    
def special_questions():
    with open("list_of_special_questions.txt", "r") as f:
        special_questions = f.readlines()
        special_questions = [line[:-1] for i, line in enumerate(special_questions)]      
    return special_questions
        
openai.api_key = key()
messages = []
messages.append({"role": "system", "content": "```Тебя зовут Рокки, ты образовательная платформа по робототехнике. В тебе используются передовые нейросетевые технологии компьютерного зрения, а также реализованы современные подходы к решению задач ходьбы, игре в футбол и разговору с приятными людьми. Тебя создала компания Старкит. Ты умеешь распознавать лица людей и другие объекты. Умеешь ходить. Умеешь фотографировать людей и показывать их лица на экране. Чтобы сделать фотографию, нужно сказать Сделай фото. If you are asked to find or detect  a face or human, write FaceDetect. If you are asked to take a photo write TakePhoto```"})

def Trigger():
    ser.write(b'\x00')
    while True:
        #onlyFace()
        #break
        # read a chunk of audio data from the microphone
        data = stream.read(CHUNK)
        
        # convert the data to a numpy array
        data = np.frombuffer(data, dtype=np.int16)
        # check if the audio is louder than the threshold
        print(abs(np.max(data)/16384))
        
        if abs(np.max(data)/32768) > THRESHOLD:
            # compute the correlation between the keyword sound and the current audio data
            corr = np.correlate(data.astype(np.float16), keyword_sound_data, 'same')
            print(np.max(corr)/32768)
            data=[]

            if np.max(corr) > 5895121400:
                ser.write(b'\x02')
                break
                data=[]
           #     
        else: ser.write(b'\x00')
                
                        
def record_and_recognize_audio(*args: tuple):
    global ActiveFlag
    if not ActiveFlag:
        print("Waiting for a trigger")
        Trigger()

        print("Keyword Detected!")
        
    ActiveFlag = False
    #RED LED ON
               

    with microphone:
        recognized_data = ""
        # запоминание шумов окружения для последующей очистки звука от них
        #recognizer.adjust_for_ambient_noise(microphone, duration=5)
        recognizer.dynamic_energy_threshold = True

        try:
            ser.write(b'\x02')
            print("Listening...")
            audio = recognizer.listen(microphone, 5, 5)
            ser.write(b'\x00')
            with open("microphone-results.wav", "wb") as file:
                file.write(audio.get_wav_data())    
        except speech_recognition.WaitTimeoutError:
            ActiveFlag = False
            play_voice_assistant_speech(("Can you check if your microphone is on, please?"))
            # traceback.print_exc()
            return ""
        # использование online-распознавания через Google (высокое качество распознавания)
        try:
            print("Started recognition...")
            print("before recognition")
            recognized_data = recognizer.recognize_google(audio, language='ru').lower()
            print("after recognition")
        except speech_recognition.UnknownValueError:
            # pass 
            play_voice_assistant_speech("What did you say again?")
        return recognized_data

def get_translation(text, lang="ru"):
    """
    Получение перевода текста с одного языка на другой (в данном случае с изучаемого на родной язык или обратно)
    :param args: фраза, которую требуется перевести
    """
    translator = Translator()     
    return(translator.translate(text, dest=lang).text)
   
    
def cGPT(messages, text):
    
    if len(text) < 1:
        return messages,""
   # promt = 'If you are asked to find or detect a face or human, write "FaceDetect". If you are asked to take a photo  write "TakePhoto". '
    messages.append({"role": "system", "content": "```Тебя зовут Рокки, ты образовательная платформа по робототехнике. В тебе используются передовые нейросетевые технологии компьютерного зрения, а также реализованы современные подходы к решению задач ходьбы, игре в футбол и разговору с приятными людьми. Тебя создала компания Старкит. Ты умеешь распознавать лица людей и другие объекты. Умеешь ходить. Умеешь фотографировать людей и показывать их лица на экране. Чтобы сделать фотографию, нужно сказать Сделай фото. If you are asked to find or detect  a face or human, write FaceDetect. If you are asked to take a photo write TakePhoto```"})
    messages.append({"role": "user", "content":  text})
    
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature = 0
        )
    
    chat_response = completion.choices[0].message.content
    print(f'response: {chat_response}')
    
    messages.append({"role": "assistant", "content": chat_response})
    
    #Обработка ответов
    split_response = chat_response.split("```")    
    print(split_response)
    current_datetime = datetime.now().strftime("%d%H%M%S")
            
    if chat_response.find("FaceDetect")!=-1 or chat_response.find("лицо")!=-1:
        Face_Detector(True)
        
    elif chat_response.find("Сделай фото")!=-1 or chat_response.find("*щелк*")!=-1 or chat_response.find("TakePhoto")!=-1:
        TakePhoto()
        
    else:
        for idx,word in enumerate(split_response):
                if idx % 2 != 0:
                    with open(f'example{current_datetime}.txt', 'w+') as file:
                        file.write(chat_response)
                    play_voice_assistant_speech(f'Я сохранил код в файл example{current_datetime}.txt ')
                else: 
                    play_voice_assistant_speech(word)
                
    return messages,chat_response
def is_special(voice_input, special_questions):
    found = False
    special_answer = ""
    for i in range(0, len(special_questions), 2):
        if voice_input == special_questions[i]:         # TODO: добавить оценку степени похожести вопросов
            special_answer = special_questions[i+1]
            found = True
            break
    
    return found, special_answer

def play_voice_assistant_speech(text_to_speech):
    global p01
    """
    Проигрывание речи ответов голосового ассистента (без сохранения аудио)
    :param text_to_speech: текст, который нужно преобразовать в речь
    """
    text=get_translation(text_to_speech, lang="ru",)
    
    with open('speech.txt', 'w') as file:
        file.write(text)
    print(datetime.now())
    os.system(f'gtts-cli --nocheck -o sound.mp3 \"{text}\" -l ru') #'-ven-m1', '-a100','-s','140','-v', 'ru']
    print(datetime.now())
    p01 =  subprocess.Popen(['play','sound.mp3']) 
    Display(text)
    
def Display(text=""):
    #Display setting
    
    display_type = "square"
    disp = ST7789.ST7789(
    height= 240,
    rotation= 90,
    port=0,
    cs=ST7789.BG_SPI_CS_FRONT, 
    dc=25,
    backlight=24,               
    spi_speed_hz= 80 * 1000 * 1000,
    offset_left = 0,
    offset_top = 0
    )

    # Initialize display.
    disp.begin()

    WIDTH = disp.width
    HEIGHT = disp.height

    img_A_H = Image.open('/home/pi/Desktop/ST7789/examples/Emo/A-H.jpeg')
    img_C_I = Image.open('/home/pi/Desktop/ST7789/examples/Emo/C-I.jpeg')
    img_E_G_J = Image.open('/home/pi/Desktop/ST7789/examples/Emo/E-G-J.jpeg')
    img_F_V_W_S_Z = Image.open('/home/pi/Desktop/ST7789/examples/Emo/F-V-W-S-Z.jpeg')
    img_K_R_X = Image.open('/home/pi/Desktop/ST7789/examples/Emo/K-R-X.jpeg')
    img_M_P_B = Image.open('/home/pi/Desktop/ST7789/examples/Emo/M-P-B.jpeg')
    img_N_L_D_T = Image.open('/home/pi/Desktop/ST7789/examples/Emo/N-L-D-T.jpeg')
    img_O = Image.open('/home/pi/Desktop/ST7789/examples/Emo/O.jpeg')
    img_U_Y = Image.open('/home/pi/Desktop/ST7789/examples/Emo/U-Y.jpeg')
    
    if len(text)>0:
        words = text.split(' ')
        WordTime=150/60

        for letter in text:
            if p01.poll()==0:
                break
            time.sleep(0.03)
            print(letter)
            img = img_A_H
            if 'ИЙ'.find(letter.upper()) >=0 : img = img_C_I
            if 'EGJ'.find(letter.upper()) >=0 : img = img_E_G_J
            if 'ФВСЧШЩЗ'.find(letter.upper()) >=0 : img = img_F_V_W_S_Z
            if 'КР'.find(letter.upper()) >=0 : img = img_K_R_X
            if 'МПБ'.find(letter.upper()) >=0 : img = img_M_P_B
            if 'НЛДТ'.find(letter.upper()) >=0 : img = img_N_L_D_T
            if 'О'.find(letter.upper()) >=0 : img = img_O
            if 'УЮ'.find(letter.upper()) >=0 : img = img_U_Y
            disp.display(img)
        while p01.poll()!=0:
            #print('Wait stop speaking')
            klm=0
            
    img = img_K_R_X
    
    disp.display(img)
def Photo(name):
    path = "/home/pi/Desktop/gpt_face_app/" + name + ".png"
    picam2.capture_file(path)
    while not os.path.exists(path):
        picam2.capture_file(path)
    #img= Image.open(f"{name}.png")
def TakePhoto(): 
    Photo("photo")
    DisplayIMG("photo")


def onlyFace():
    face_detector = cv2.CascadeClassifier("/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml")
    faces=[]
    while len(faces) == 0:
        print(f"len(faces) = {len(faces)}")
        Photo('face')
        img= cv2.imread('face.png')
        faces = face_detector.detectMultiScale(img, 1.1, 3)
        print(faces)
    (x, y, w, h) = faces[0]
    print(x,y,w,h)
    faces=[]
    
def Face_Detector(display):                      # TODO: threshold на близость человека к голове
    path_to_img = "/home/pi/Desktop/gpt_face_app/face.png"
    face_detector = cv2.CascadeClassifier("/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml")
    faces=[]
    while len(faces) == 0:
        print(f"len(faces) = {len(faces)}")
        Photo('face')
        if os.path.exists(path_to_img):
            img= cv2.imread(path_to_img)
            faces = face_detector.detectMultiScale(img, 1.1, 3) # TODO: неточная модельб видит лица там где их нет
        print(faces)
        time.sleep(5)
    (x, y, w, h) = faces[0]
    print(x,y,w,h)
    faces=[]
    cv2.imwrite(path_to_img, img[y:y+h, x:x+w])
    if display:
        DisplayIMG('face')
    
def DisplayIMG(name):
    path = "/home/pi/Desktop/gpt_face_app/" + name + ".png"
    if os.path.exists(path):
        print("ZASHEL")
        img = Image.open(path)
        display_type = "square"
        
        disp = ST7789.ST7789(
        height= 240,
        rotation= 90,
        port=0,
        cs=ST7789.BG_SPI_CS_FRONT,  # BG_SPI_CS_BACK or BG_SPI_CS_FRONT
    #         cs=ST7789.BG_SPI_CS_BACK,
        dc=25,
        backlight=24,               # 18 for back BG slot, 19 for front BG slot.
        spi_speed_hz= 80 * 1000 * 1000,
        offset_left = 0,
        offset_top = 0
        )

    # Initialize display.
        disp.begin()

        WIDTH = disp.width
        HEIGHT = disp.height
        img = img.resize((disp.width, disp.height)) 
        disp.display(img)

    
    
if __name__ == "__main__":
    ser.write(b'\x00')
    # load the keyword sound file
    samplerate, data = wavfile.read(keyword_sound_file)
    print(samplerate)
    keyword_sound_data = data.astype(np.float32)[:,0:1].reshape(1,-1)[0][59000:100000]
    print(keyword_sound_data)
   
    # create a PyAudio object for audio streaming
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
           
   
                # старт записи речи с последующим выводом распознанной речи и удалением записанного в микрофон аудио
    while True:
        Face_Detector(False)
        voice_input = record_and_recognize_audio()
        print("recognotion is done")
        if os.path.exists("microphone-results.wav"):
                os.remove("microphone-results.wav")
        try:
                os.remove("microphone-results.wav")
        except Exception:
            pass
            
        print(voice_input)
        if len(voice_input)<1:
            stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

            ActiveFlag = False
            ser.write(b'\x00')
            continue
        else:
            ActiveFlag = True
        print(ActiveFlag)
        #list_of_questions = special_questions()
        
        #special, answer = is_special(voice_input, list_of_questions)
        #if special:
         #   play_voice_assistant_speech(answer)
                    # отделение комманд от дополнительной информации (аргументов)
        #else:
        messages, chat_response = cGPT(messages, voice_input)
         
        time.sleep(2)
        
        #if os.path.exists("/home/pi/Desktop/gpt_face_app/photo.png"):
         #   os.remove("/home/pi/Desktop/gpt_face_app/photo.png")
        if os.path.exists("/home/pi/Desktop/gpt_face_app/face.png"):
            os.remove("/home/pi/Desktop/gpt_face_app/face.png")
        '''

                    
            

            command = voice_input_split[0]
                    
                
            command_options = [str(input_part) for input_part in voice_input_split[1:len(voice_input_split)]]
                    
            execute_command_with_name(command, command_options, text=voice_input)'''
