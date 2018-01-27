import os
import sys
import socket
import pyaudio
import colorsys
import numpy as np
import speech_recognition as sr
import subprocess as sp
import pigpio
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from PIL import Image

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\Tad\\Desktop\\TargetedAdvertising-dc956f1a9b6b.json"

ip = "192.168.1.10"
pi = pigpio.pi(ip, 8888)  # HOST, PORT
print(pi.connected)
RED_PIN = 10
GREEN_PIN = 9
BLUE_PIN = 11


def setRedInten(redVal):
    pi.set_PWM_dutycycle(RED_PIN, redVal)
    pi.write(10, 1)
    pi.write(9, 0)
    pi.write(11, 0)


def setGreenInten(greenVal):
    pi.write(9, 1)
    pi.write(10, 0)
    pi.write(11, 0)


def setBlueInten(blueVal):
    pi.set_PWM_dutycycle(BLUE_PIN, blueVal)
    pi.write(11, 1)
    pi.write(9, 0)
    pi.write(10, 0)


def ipcheck():
    try:
        status, result = sp.getstatusoutput('ping ' + ip)
        hostname = socket.gethostbyaddr(ip)
        print (hostname)
        if status == 0 and "pi" in hostname:
            print('tadPi@ ' + ip + ' is UP')
            print(result)
        else:
            print('tadPi@ ' + ip + ' is DOWN')
    except Exception as e:
        print("\nCouldn't contact host " + str(e))


def makeSentimentImg(sentiment, text):
    if -1.0 <= sentiment.score <= -0.25:
        print("\nBad: {}".format(text))
        setRedInten(255)
    elif -0.25 <= sentiment.score <= 0.25:
        print("\nNeutral: {}".format(text))
        setBlueInten(255)
    elif 0.25 <= sentiment.score <= 1.0:
        print("\nGood: {}".format(text))
        setGreenInten(255)

    # hsvColor = (sentiment.score, sentiment.magnitude, 1)
    # rgbConversion = colorsys.hsv_to_rgb((round(sentiment.score),1), (round(sentiment.magnitude),1), 1)
    # print (rgbConversion)

    array = np.zeros([720, 1080, 3], dtype=np.uint8)
    array[:, :] = [0, 0, 255]  # 4 = alpha channel
    imgnew = Image.fromarray(array)
    imgnew.save('color.png')
    imgnew = Image.open('color.png')
    imgnew.show()


def printOver(str):
    sys.stdout.write("\r" + (str))
    sys.stdout.flush()


def record():
    r = sr.Recognizer()
    try:
        with sr.Microphone(device_index=1, sample_rate=48000) as source:
            printOver('listening...')
            # r.adjust_for_ambient_noise(source)
            # r.energy_threshold #edit
            audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            printOver('understood...')

            try:
                document = types.Document(
                    content=text,
                    type=enums.Document.Type.PLAIN_TEXT)
                client = language.LanguageServiceClient()
                printOver('interpreting...')
                sentiment = client.analyze_sentiment(document=document).document_sentiment
                sentimentScr = int(round((sentiment.score + 1) * (255 / 2)))
                sentimentMag = int(round((sentiment.magnitude + 1) * (255 / 2)))
                printOver('feeling...')
                print('\nSentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))
                print('SentimentScr: ' + str(sentimentScr))
                print('SentimentMag: ' + str(sentimentMag))

                try:
                    makeSentimentImg(sentiment, text)  ##generates and displays image
                except Exception as e:
                    print("\nCouldn't create image " + str(e))

            except Exception as e:
                print('\nFailed to process sentiment ' + str(e))

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

    except Exception as e:
        print('\nSomething went wrong ' + str(e))


# system and input devices check
ipcheck()
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(info['index'], info['name'])

while True:
    record()
