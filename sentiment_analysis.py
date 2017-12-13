import os
import time
import colorama
import pyaudio
import speech_recognition as sr
import sounddevice as sd
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:\\Users\\Tad\\Desktop\\TargetedAdvertising-dc956f1a9b6b.json"
from colorama import init, Fore, Back, Style

def sentimentScore(sentiment, text):
    init()
    if -1.0 <= sentiment.score <= -0.25:
        print('\033[91m' + ("Bad: {}".format(text)) + '\033[91m')
        # print (Back.RED + ("Bad: {}".format(text)))

    elif -0.25 <= sentiment.score <= 0.25:
        print('\033[94m' + ("Neutral: {}".format(text)) + '\033[94m')
        # print (Back.CYAN + ("Neutral: {}".format(text)))

    elif 0.25 <= sentiment.score <= 1.0:
        print('\033[92m' + ("Good: {}".format(text)) + '\033[92m')
        # print (Back.GREEN + ("Good: {}".format(text)))

def record():
    r = sr.Recognizer()
    try:
        with sr.Microphone(device_index=1) as source:
            print("Recording")
            # print(sd.query_devices())
            audio = r.listen(source)
            r.recognize_google(audio)

            # Instantiates a client
            client = language.LanguageServiceClient()

            # The text to analyze
            text = r.recognize_google(audio)
            document = types.Document(
                content=text,
                type=enums.Document.Type.PLAIN_TEXT)

            # Detects the sentiment of the text
            sentiment = client.analyze_sentiment(document=document).document_sentiment
            sentimentScore(sentiment, text)
            print ('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

#check input devices
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(info['index'], info['name'])
while True:
    record()
    time.sleep(10)

