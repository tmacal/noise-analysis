import os
import sys
import time
import numpy as np
import speech_recognition as sr
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:\\Users\\Tad\\Desktop\\TargetedAdvertising-dc956f1a9b6b.json"
from PIL import Image
# from colorama import init, Fore, Back, Style ## include - init()
# from pocketsphinx import pocketsphinx

def makeSentimentImg(sentiment, text):
    if -1.0 <= sentiment.score <= -0.25:
        print("\nBad: {}".format(text))
        # array = np.zeros([720, 1080, 3], dtype=np.uint8)
        # array[:, :] = [255, 0, 0]  # 4 = alpha channel
        # imgbad = Image.fromarray(array)
        # imgbad.save('testr.png')
        imgbad = Image.open('testr.png')
        imgbad.show()

    elif -0.25 <= sentiment.score <= 0.25:
        print("\nNeutral: {}".format(text))
        # array = np.zeros([720, 1080, 3], dtype=np.uint8)
        # array[:, :] = [0, 0, 255]  # 4 = alpha channel
        # imgneut = Image.fromarray(array)
        # imgneut.save('testb.png')
        imgneut = Image.open('testb.png')
        imgneut.show()

    elif 0.25 <= sentiment.score <= 1.0:
        print("\nGood: {}".format(text))
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
        with sr.Microphone(device_index=1) as source:
            # print('recording...')
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

                # print('feeling...')
                printOver('feeling...')
                makeSentimentImg(sentiment, text) ##generates and displays image
                print('\nSentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))
                print('SentimentScr: ' + str(sentimentScr))
                print('SentimentMag: ' + str(sentimentMag))

            except Exception as e:
                print('\nFailed to process sentiment' + str(e))

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

        # try:
        #     text = r.recognize_sphinx(audio)
        #     printOver('understood...')
        # except sr.UnknownValueError:
        #     print("Sphinx could not understand audio")
        # except sr.RequestError as e:
        #     print("Sphinx error; {0}".format(e))

    except Exception as e:
        print('\nSomething went wrong' + str(e)) #general error handler

# #check input devices
# p = pyaudio.PyAudio()
# for i in range(p.get_device_count()):
#     info = p.get_device_info_by_index(i)
#     print(info['index'], info['name'])
while True:
    record()