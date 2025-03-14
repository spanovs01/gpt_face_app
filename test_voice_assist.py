import requests
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

p01=''


recognizer = speech_recognition.Recognizer()
microphone = speech_recognition.Microphone()
CHUNK = 2048  # size of audio chunk for processing
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100  # sample rate of audio stream
RECORD_SECONDS = 0.5  # number of seconds to record audio for
THRESHOLD = 0.1 # threshold for sound detection
keyword_sound_file = "key_phrase_Roki.wav"

ActiveFlag=False

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

def key():
    with open("gpt_code.txt", "r") as f:
        key = f.readlines()[0][:-1]
    return key
    
def special_questions():
    with open("list_of_special_questions.txt", "r") as f:
        special_questions = f.readlines()
        special_questions = [line[:-1] for i, line in enumerate(special_questions)]      
    return special_questions

messages = []
messages.append({"role": "system", "content": "```Тебя зовут Рокки, ты образовательная платформа по робототехнике. В тебе используются передовые нейросетевые технологии компьютерного зрения, а также реализованы современные подходы к решению задач ходьбы, игре в футбол и разговору с приятными людьми. Тебя создала компания Старкит. Ты умеешь распознавать лица людей и другие объекты. Умеешь ходить. Умеешь фотографировать людей и показывать их лица на экране. Чтобы сделать фотографию, нужно сказать Сделай фото. If you are asked to find or detect  a face or human, write FaceDetect. If you are asked to take a photo write TakePhoto```"})

def Trigger(keyword_sound_data):
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
                
                        
def record_and_recognize_audio(keyword):
    global ActiveFlag
    if not ActiveFlag:
        print("Waiting for a trigger")
        Trigger(keyword)

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
    # Если текст пустой, возвращаем текущие сообщения и пустой ответ
    if len(text) < 1:
        return messages, ""

    # Добавляем системное сообщение и сообщение пользователя
    messages.append({
        "role": "system",
        "content": "```Тебя зовут Рокки, ты образовательная платформа по робототехнике. В тебе используются передовые нейросетевые технологии компьютерного зрения, а также реализованы современные подходы к решению задач ходьбы, игре в футбол и разговору с приятными людьми. Тебя создала компания Старкит.```"
    })
    messages.append({"role": "user", "content": text})

    # Вызов API DeepSeek
    API_KEY = key()  # Замените на ваш API-ключ
    
    url = "https://api.deepseek.com/chat/completions"

    # Заголовки запроса
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # Тело запроса
    # data = {
    #     "model": "deepseek-chat",
    #     "messages": messages,
    #     "stream": False
    # }
    data = {}
    data["model"] = "deepseek-chat"
    data["messages"] = messages
    data["stream"] = False
    data["temperature"] = 0
    data["max_tokens"] = 150

    # Отправка POST-запроса
    response = requests.post(url, headers=headers, json=data)
    print(response)
    # Обработка ответа
    if response.status_code == 200:
        result = response.json()
        chat_response = result["choices"][-1]["message"]["content"]
    else:
        print("Ошибка:", response.status_code, response.text)
        return messages, ""

    # Добавляем ответ ассистента в историю сообщений
    messages.append({"role": "assistant", "content": chat_response})

    # Обработка ответов
    split_response = chat_response.split("```")
    print(split_response)
    current_datetime = datetime.now().strftime("%d%H%M%S")

    for idx, word in enumerate(split_response):
        if idx % 2 != 0:
            # Сохраняем код в файл
            with open(f'example{current_datetime}.txt', 'w+') as file:
                file.write(chat_response)
            play_voice_assistant_speech(f'Я сохранил код в файл example{current_datetime}.txt')
        else:
            # Воспроизводим текст голосом
            play_voice_assistant_speech(word)

    return messages, chat_response
    
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
    p01 = subprocess.Popen(['play','sound.mp3'])
    Display(text=text)
    
def Display(text=""):
    global disp
    img_A_H = Image.open('/home/pi/Desktop/ST7789/examples/Emo/A-H.jpeg')
    img_C_I = Image.open('/home/pi/Desktop/ST7789/examples/Emo/C-I.jpeg')
    img_E_G_J = Image.open('/home/pi/Desktop/ST7789/examples/Emo/E-G-J.jpeg')
    img_F_V_W_S_Z = Image.open('/home/pi/Desktop/ST7789/examples/Emo/F-V-W-S-Z.jpeg')
    img_K_R_X = Image.open('/home/pi/Desktop/ST7789/examples/Emo/K-R-X.jpeg')
    img_M_P_B = Image.open('/home/pi/Desktop/ST7789/examples/Emo/M-P-B.jpeg')
    img_N_L_D_T = Image.open('/home/pi/Desktop/ST7789/examples/Emo/N-L-D-T.jpeg')
    img_O = Image.open('/home/pi/Desktop/ST7789/examples/Emo/O.jpeg')
    img_U_Y = Image.open('/home/pi/Desktop/ST7789/examples/Emo/U-Y.jpeg')
    img_initial = Image.open('/home/pi/Desktop/Startup/I_240_240_2.png')

    if len(text)>0:
        words = text.split(' ')
        WordTime=150/60

        for letter in text:
            # print(letter)
            # if p01.poll()==0:
            #     break
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
            time.sleep(0.06)
        print("displaying letters [DONE]")
        # while p01.poll()!=0:
            # print('Wait stop speaking')
            # klm=0
            
    img = img_initial
    
    disp.display(img)
    
if __name__ == "__main__":
    ser.write(b'\x00')
    # load the keyword sound file
    samplerate, data = wavfile.read(keyword_sound_file)
    RATE = samplerate
    keyword = data
    print(samplerate)
    # keyword_sound_data = data.astype(np.float32)[:,0:1].reshape(1,-1)[0][59000:100000]
    print(keyword)
   
    # create a PyAudio object for audio streaming
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
           
   
                # старт записи речи с последующим выводом распознанной речи и удалением записанного в микрофон аудио
    while True:
        voice_input = record_and_recognize_audio(keyword)
        print("recognotion is done")
        if os.path.exists("microphone-results.wav"):
            os.remove("microphone-results.wav")
        # try:
        #         os.remove("microphone-results.wav")
        # except Exception:
        #     pass
            
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
        print(f"answer: {chat_response}")
         
        time.sleep(2)
        '''

                    
            

            command = voice_input_split[0]
                    
                
            command_options = [str(input_part) for input_part in voice_input_split[1:len(voice_input_split)]]
                    
            execute_command_with_name(command, command_options, text=voice_input)'''
