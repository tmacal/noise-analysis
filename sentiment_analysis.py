import os
import sys
import pyaudio
import numpy as np
import speech_recognition as sr
import subprocess as sp
import pigpio
from googleads import adwords
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:\\Users\\Tad\\Desktop\\TargetedAdvertising-dc956f1a9b6b.json"
from PIL import Image

##set up pigpio daemon on raspberryPi
# @reboot         /usr/local/bin/pigpiod
# Use
#
# sudo crontab -e
#
# to edit the root crontab and add that line to the end. Then ctrl-o return ctrl-x to exit.
ip = "192.168.1.10"

pi = pigpio.pi(ip, 8888) #HOST, PORT
print(pi.connected)

RED_PIN = 13
GREEN_PIN = 15
BLUE_PIN = 17

def setRedInten(redVal):
    pi.set_PWM_dutycycle(RED_PIN, redVal)
def setGreenInten(greenVal):
    pi.set_PWM_dutycycle(GREEN_PIN, greenVal)
def setBlueInten(blueVal):
    pi.set_PWM_dutycycle(BLUE_PIN, blueVal)

def ipcheck():
    status, result = sp.getstatusoutput('ping ' + ip)
    if status == 0:
        print('tadPi@ ' + ip + ' is UP')
        print(result)
    else:
        print('tadPi@ ' + ip + ' is DOWN')

def makeSentimentImg(sentiment, text):
    if -1.0 <= sentiment.score <= -0.25:
        print("\nBad: {}".format(text))
        setRedInten(255)
        # array = np.zeros([720, 1080, 3], dtype=np.uint8)
        # array[:, :] = [255, 0, 0]  # 4 = alpha channel
        # imgbad = Image.fromarray(array)
        # imgbad.save('testr.png')
        imgbad = Image.open('testr.png')
        imgbad.show()

    elif -0.25 <= sentiment.score <= 0.25:
        print("\nNeutral: {}".format(text))
        setBlueInten(255)
        # array = np.zeros([720, 1080, 3], dtype=np.uint8)
        # array[:, :] = [0, 0, 255]  # 4 = alpha channel
        # imgneut = Image.fromarray(array)
        # imgneut.save('testb.png')
        imgneut = Image.open('testb.png')
        imgneut.show()

    elif 0.25 <= sentiment.score <= 1.0:
        print("\nGood: {}".format(text))
        setGreenInten(255)
        # array = np.zeros([720, 1080, 3], dtype=np.uint8)
        # array[:, :] = [0, 128, 0]  # 4 = alpha channel
        # imggood = Image.fromarray(array)
        # imggood.save('testg.png')
        imggood = Image.open('testg.png')
        imggood.show()

def printOver(str):
    sys.stdout.write("\r" + (str))
    sys.stdout.flush()

def makeImg(sentimentScr):
    array = np.zeros([720, 1080, 3], dtype=np.uint8)
    array[:, :] = [sentimentScr, sentimentScr, sentimentScr] #RGB values from range 0 - 255
    madeImg = Image.fromarray(array)
    madeImg.save('madeImg.png')
    madeImg = Image.open('madeImg.png')
    madeImg.show()
    madeImg.close()

def record():
    r = sr.Recognizer()
    try:
        with sr.Microphone(device_index=1, sample_rate = 48000) as source:
            printOver('listening...')
            # r.adjust_for_ambient_noise(source)
            # r.energy_threshold ##edit*
            audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            printOver('understood...')

            try:
                document = types.Document(
                    content=text,
                    type=enums.Document.Type.PLAIN_TEXT)
                # instantiates client
                client = language.LanguageServiceClient()
                # Detects sentiment
                printOver('interpreting...')
                sentiment = client.analyze_sentiment(document=document).document_sentiment
                sentimentScr = int(round((sentiment.score + 1) *(255/2)))
                sentimentMag = int(round((sentiment.score + 1) *(255/2)))
                printOver('feeling...')
                makeSentimentImg(sentiment, text) ##generates and displays image
                # makeColor(sentimentScr)
                print('\nSentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))
                print('SentimentScr: ' + str(sentimentScr))
                print('SentimentMag: ' + str(sentimentMag))

            except Exception as e:
                print('\nFailed to process sentiment ' + str(e))

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

    except Exception as e:
        print('\nSomething went wrong ' + str(e)) #general error handler

#system and input devices check
ipcheck()
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(info['index'], info['name'])

while True:
    record()