import os
import sys
import time
import pyaudio
import numpy as np
import speech_recognition as sr
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:\\Users\\Tad\\Desktop\\TargetedAdvertising-dc956f1a9b6b.json"
from colorama import init, Fore, Back, Style
from PIL import Image

def makeSentimentImg(sentiment, text):
    init()
    if -1.0 <= sentiment.score <= -0.25:
        print (Back.RED + ("\nBad: {}".format(text)))
        # array = np.zeros([720, 1080, 3], dtype=np.uint8)
        # array[:, :] = [255, 0, 0]  # 4 = alpha channel
        # imgbad = Image.fromarray(array)
        # imgbad.save('testr.png')
        imgbad = Image.open('testr.png')
        imgbad.show()
        imgbad.close()

    elif -0.25 <= sentiment.score <= 0.25:
        print (Back.CYAN + ("\nNeutral: {}".format(text)))
        # array = np.zeros([720, 1080, 3], dtype=np.uint8)
        # array[:, :] = [0, 0, 255]  # 4 = alpha channel
        # imgneut = Image.fromarray(array)
        # imgneut.save('testb.png')
        imgneut = Image.open('testb.png')
        imgneut.show()
        imgneut.close()

    elif 0.25 <= sentiment.score <= 1.0:
        print (Back.GREEN + ("\nGood: {}".format(text)))
        # array = np.zeros([720, 1080, 3], dtype=np.uint8)
        # array[:, :] = [0, 128, 0]  # 4 = alpha channel
        # imggood = Image.fromarray(array)
        # imggood.save('testg.png')
        imggood = Image.open('testg.png')
        imggood.show()
        imggood.close()

def printOver(str):
    sys.stdout.write("\r" + (str))
    sys.stdout.flush()

def progressBar(text):
    for i in range(len(text)):
        time.sleep(1)
        sys.stdout.write("\r%d%%" % (i/len(text)*100))
        sys.stdout.flush()

def makeImg(sentimentScr):
    array = np.zeros([720, 1080, 3], dtype=np.uint8)
    'R                           G                         B'
    array[:, :] = [sentimentScr, sentimentScr, sentimentScr]
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
            printOver('recording...')
            # r.adjust_for_ambient_noise(source)
            # r.energy_threshold ##edit*
            audio = r.listen(source)
            r.recognize_google(audio)
            # print('understood...')
            printOver('understood...')

            # Instantiates a client
            client = language.LanguageServiceClient()

            # The text to analyze
            text = r.recognize_google(audio)
            # progressBar(text) #percentage progress bar
            # print('interpreting...')
            printOver('interpreting...')
            document = types.Document(
                content=text,
                type=enums.Document.Type.PLAIN_TEXT)

            # Detects sentiment
            sentiment = client.analyze_sentiment(document=document).document_sentiment
            sentimentScr = int(round((sentiment.score + 1) *(255/2)))
            sentimentMag = int(round((sentiment.score + 1) *(255/2)))

            # print('feeling...')
            printOver('feeling...')
            makeSentimentImg(sentiment, text) ##displays image
            print ('\nSentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))
            print('SentimentScr: ' + str(sentimentScr))
            print('SentimentMag: ' + str(sentimentMag))

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

# #check input devices
# p = pyaudio.PyAudio()
# for i in range(p.get_device_count()):
#     info = p.get_device_info_by_index(i)
#     print(info['index'], info['name'])
while True:
    record()
    # time.sleep(10)