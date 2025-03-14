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


class VoiceAssistant():
    def __init__(self):
        self.init_serial()
        self.p01=''
        self.recognizer = speech_recognition.Recognizer()
        self.microphone = speech_recognition.Microphone()
        self.set_audio_params()
        self.ActiveFlag=False
        self.init_display()
        self.set_display_images()
        self.messages = []
        self.messages.append({"role": "system", "content": "```Тебя зовут Рокки, ты образовательная платформа по робототехнике. В тебе используются передовые нейросетевые технологии компьютерного зрения, а также реализованы современные подходы к решению задач ходьбы, игре в футбол и разговору с приятными людьми. Тебя создала компания Старкит. Ты не можешь генерировать текст с такими символами как \n, * и тому подобное. Ты генерируешь только короткие ответы!```"})
        # create a PyAudio object for audio streaming
        self.audio = pyaudio.PyAudio()
        self.translator = Translator()
        # load the keyword sound file
        self.RATE, self.keyword = wavfile.read(self.keyword_sound_file)

        # запрос
        self.url = "https://api.deepseek.com/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.key()}"
        }
        self.response_data = {}
        self.response_data["model"] = "deepseek-chat"
        self.response_data["stream"] = False
        self.response_data["temperature"] = 0
        self.response_data["max_tokens"] = 150

    def init_serial(self):
        self.ser = serial.Serial ('/dev/ttyAMA1') #Open named port
        self.ser.baudrate = 115200 #Set baud rate to 9600

    def set_audio_params(self):
        self.CHUNK = 2048  # size of audio chunk for processing
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 44100  # sample rate of audio stream
        self.RECORD_SECONDS = 0.5  # number of seconds to record audio for
        self.THRESHOLD = 0.1 # threshold for sound detection
        self.keyword_sound_file = "key_phrase_Roki.wav"

    def init_display(self):
        #Display setting
        # display_type = "square"
        self.disp = ST7789.ST7789(
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
        self.disp.begin()

        # WIDTH = disp.width
        # HEIGHT = disp.height
    
    def set_display_images(self):
        self.img_A_H = Image.open('/home/pi/Desktop/ST7789/examples/Emo/A-H.jpeg')
        self.img_C_I = Image.open('/home/pi/Desktop/ST7789/examples/Emo/C-I.jpeg')
        self.img_E_G_J = Image.open('/home/pi/Desktop/ST7789/examples/Emo/E-G-J.jpeg')
        self.img_F_V_W_S_Z = Image.open('/home/pi/Desktop/ST7789/examples/Emo/F-V-W-S-Z.jpeg')
        self.img_K_R_X = Image.open('/home/pi/Desktop/ST7789/examples/Emo/K-R-X.jpeg')
        self.img_M_P_B = Image.open('/home/pi/Desktop/ST7789/examples/Emo/M-P-B.jpeg')
        self.img_N_L_D_T = Image.open('/home/pi/Desktop/ST7789/examples/Emo/N-L-D-T.jpeg')
        self.img_O = Image.open('/home/pi/Desktop/ST7789/examples/Emo/O.jpeg')
        self.img_U_Y = Image.open('/home/pi/Desktop/ST7789/examples/Emo/U-Y.jpeg')
        self.img_initial = Image.open('/home/pi/Desktop/Startup/I_240_240_2.png')

    def key(self):
        with open("gpt_code.txt", "r") as f:
            key = f.readlines()[0][:-1]
        return key

    def Trigger(self):
        self.ser.write(b'\x00')
        while True:
            # read a chunk of audio data from the microphone
            data = self.stream.read(self.CHUNK)
            
            # convert the data to a numpy array
            data = np.frombuffer(data, dtype=np.int16)
            # check if the audio is louder than the threshold
            print(abs(np.max(data)/16384))
            
            if abs(np.max(data)/32768) > self.THRESHOLD:
                # compute the correlation between the keyword sound and the current audio data
                corr = np.correlate(data.astype(np.float16), self.keyword, 'same')
                print(np.max(corr)/32768)
                data=[]

                if np.max(corr) > 5895121400:
                    self.ser.write(b'\x02')
                    break
                    data=[]
            #     
            else: self.ser.write(b'\x00')

    def record_and_recognize_audio(self):
        if not self.ActiveFlag:
            print("Waiting for a trigger")
            self.Trigger()

            print("Keyword Detected!")
            
        self.ActiveFlag = False
        #RED LED ON
                

        with self.microphone:
            recognized_data = ""
            # запоминание шумов окружения для последующей очистки звука от них
            #recognizer.adjust_for_ambient_noise(microphone, duration=5)
            self.recognizer.dynamic_energy_threshold = True

            try:
                self.ser.write(b'\x02')
                print("Listening...")
                audio = self.recognizer.listen(self.microphone, 5, 5)
                self.ser.write(b'\x00')
                with open("microphone-results.wav", "wb") as file:
                    file.write(audio.get_wav_data())    
            except speech_recognition.WaitTimeoutError:
                self.ActiveFlag = False
                self.play_voice_assistant_speech(("Can you check if your microphone is on, please?"))
                # traceback.print_exc()
                return ""
            # использование online-распознавания через Google (высокое качество распознавания)
            try:
                print("Started recognition...")
                print("before recognition")
                recognized_data = self.recognizer.recognize_google(audio, language='ru').lower()
                print(recognized_data)
                print("after recognition")
            except speech_recognition.UnknownValueError:
                # pass 
                self.play_voice_assistant_speech("What did you say again?")
            return recognized_data

    def get_translation(self, text, lang="ru"):
        """
        Получение перевода текста с одного языка на другой (в данном случае с изучаемого на родной язык или обратно)
        :param args: фраза, которую требуется перевести
        """
        return(self.translator.translate(text, dest=lang).text)
    
    def play_voice_assistant_speech(self, text_to_speech):
        """
        Проигрывание речи ответов голосового ассистента (без сохранения аудио)
        :param text_to_speech: текст, который нужно преобразовать в речь
        """
        text=self.get_translation(text_to_speech, lang="ru",)
        
        with open('speech.txt', 'w') as file:
            file.write(text)
        print(datetime.now())
        os.system(f'gtts-cli --nocheck -o sound.mp3 \"{text}\" -l ru') #'-ven-m1', '-a100','-s','140','-v', 'ru']
        print(datetime.now())
        self.p01 = subprocess.Popen(['play','sound.mp3'])
        self.Display(text=text)

    def Display(self, text=""):
        if len(text)>0:
            words = text.split(' ')
            WordTime=150/60
            for iter in range(len(text)):
                if iter % 100 == 0:
                    letter = text[iter]
                    # print(letter)
                    if self.p01.poll()==0:
                        print("DONE displaying images")
                        break
                    img = self.img_A_H
                    if 'ИЙ'.find(letter.upper()) >=0 : img = self.img_C_I
                    if 'EGJ'.find(letter.upper()) >=0 : img = self.img_E_G_J
                    if 'ФВСЧШЩЗ'.find(letter.upper()) >=0 : img = self.img_F_V_W_S_Z
                    if 'КР'.find(letter.upper()) >=0 : img = self.img_K_R_X
                    if 'МПБ'.find(letter.upper()) >=0 : img = self.img_M_P_B
                    if 'НЛДТ'.find(letter.upper()) >=0 : img = self.img_N_L_D_T
                    if 'О'.find(letter.upper()) >=0 : img = self.img_O
                    if 'УЮ'.find(letter.upper()) >=0 : img = self.img_U_Y
                    self.disp.display(img)
                    time.sleep(1)
                    print(img.size)
            print("displaying letters [DONE]")
            while self.p01.poll()!=0:
                # print('Wait stop speaking')
                # klm=0
                pass
                
        img = self.img_A_H
        self.disp.display(img)
    
    def cGPT(self, text):
        # Если текст пустой, возвращаем текущие сообщения и пустой ответ
        if len(text) < 1:
            return ""

        # Добавляем системное сообщение и сообщение пользователя
        self.messages.append({
            "role": "system",
            "content": "```Тебя зовут Рокки, ты образовательная платформа по робототехнике. В тебе используются передовые нейросетевые технологии компьютерного зрения, а также реализованы современные подходы к решению задач ходьбы, игре в футбол и разговору с приятными людьми. Тебя создала компания Старкит.```"
        })
        self.messages.append({"role": "user", "content": text})

        self.response_data["messages"] = self.messages

        # Отправка POST-запроса
        response = requests.post(self.url, headers=self.headers, json=self.response_data)
        print(response)
        # Обработка ответа
        if response.status_code == 200:
            result = response.json()
            chat_response = result["choices"][-1]["message"]["content"]
        else:
            print("Ошибка:", response.status_code, response.text)
            return ""

        # Добавляем ответ ассистента в историю сообщений
        self.messages.append({"role": "assistant", "content": chat_response})

        # Обработка ответов
        split_response = chat_response.split("```")
        print(split_response)
        current_datetime = datetime.now().strftime("%d%H%M%S")

        for idx, word in enumerate(split_response):
            if idx % 2 != 0:
                # Сохраняем код в файл
                with open(f'example{current_datetime}.txt', 'w+') as file:
                    file.write(chat_response)
                self.play_voice_assistant_speech(f'Я сохранил код в файл example{current_datetime}.txt')
            else:
                # Воспроизводим текст голосом
                self.play_voice_assistant_speech(word)

        return chat_response

    def main(self):
        self.ser.write(b'\x00')
        iter = 0
    
        self.stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
            
    
                    # старт записи речи с последующим выводом распознанной речи и удалением записанного в микрофон аудио
        while True:
            voice_input = self.record_and_recognize_audio()
            print("recognotion is done")
            if os.path.exists("microphone-results.wav"):
                try:
                    os.remove("microphone-results.wav")
                except Exception:
                    pass
                
            # print(voice_input)
            if len(voice_input)<1:
                self.stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)

                self.ActiveFlag = False
                self.ser.write(b'\x00')
                continue
            else:
                self.ActiveFlag = True
            print(self.ActiveFlag)
            
            chat_response = self.cGPT(voice_input)
            print(f"answer: {chat_response}")

            if iter > 10:
                self.messages.pop(0)
            self.stream.close()
            time.sleep(2)
            iter += 1
                
                        

   
    


    
    
if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.main()
    '''
    # create a PyAudio object for audio streaming
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
           
   
                # старт записи речи с последующим выводом распознанной речи и удалением записанного в микрофон аудио
    while True:
        # voice_input = record_and_recognize_audio(keyword)
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
        
        messages, chat_response = cGPT(messages, voice_input)
        print(f"answer: {chat_response}")
         
        time.sleep(2)
    

                    
           
            # command = voice_input_split[0]
                    
                
            # command_options = [str(input_part) for input_part in voice_input_split[1:len(voice_input_split)]]
                    
            # execute_command_with_name(command, command_options, text=voice_input)
    '''