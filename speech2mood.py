import os
import sys
import socket
import pyaudio
import turtle
import speech_recognition as sr
import subprocess as sp
import pigpio
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

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
    pi.set_PWM_dutycycle(GREEN_PIN, greenVal)
    pi.write(9, 1)
    pi.write(10, 0)
    pi.write(11, 0)


def setBlueInten(blueVal):
    pi.set_PWM_dutycycle(BLUE_PIN, blueVal)
    pi.write(11, 1)
    pi.write(9, 0)
    pi.write(10, 0)


def hostcheck():
    try:
        status, result = sp.getstatusoutput('ping ' + ip)
        hostname = socket.gethostbyaddr(ip)
        print(hostname)
        if status == 0 and "pi" in hostname:
            print('tadPi@ ' + ip + ' is UP')
            print(result)
        else:
            print('tadPi@ ' + ip + ' is DOWN')
    except Exception as e:
        print("\nCouldn't contact host " + str(e))


def changeSentimentColor(sentiment, text):
    if -1.0 <= sentiment.score <= -0.25:
        print("\nBad: {}".format(text))
        setRedInten(255)
    if -0.25 <= sentiment.score <= 0.25:
        print("\nNeutral: {}".format(text))
        setBlueInten(255)
    if 0.25 <= sentiment.score <= 1.0:
        print("\nGood: {}".format(text))
        setGreenInten(255)


def createTkImage(sentiment):
    turtle.screensize(canvwidth=None, canvheight=None, bg=None)
    turtle.reset()
    turtle.up()
    turtle.goto(0, -100)
    turtle.down()
    turtle.begin_fill()
    turtle.fillcolor("yellow")
    turtle.circle(100)
    turtle.end_fill()
    # drawSmile
    if 0.25 <= sentiment.score <= 1.0:
        turtle.up()
        turtle.goto(-67, -40)
        turtle.setheading(-60)
        turtle.width(5)
        turtle.down()
        turtle.circle(80, 120)
    # drawSad
    if -1.0 <= sentiment.score <= -0.25:
        turtle.up()
        turtle.goto(-67, -40)
        turtle.setheading(-120)
        turtle.width(5)
        turtle.down()
        turtle.circle(80, -120)
    # drawNeutral
    if -0.25 <= sentiment.score <= 0.25:
        turtle.up()
        turtle.goto(-67, -40)
        turtle.width(5)
        turtle.down()
        turtle.forward(140)

    turtle.fillcolor("black")

    for i in range(-35, 105, 70):
        turtle.up()
        turtle.goto(i, 35)
        turtle.setheading(0)
        turtle.down()
        turtle.begin_fill()
        turtle.circle(10)  # draw eyes
        turtle.end_fill()

    turtle.hideturtle()


def printOver(str):
    sys.stdout.write("\r" + (str))
    sys.stdout.flush()


def record():
    r = sr.Recognizer()
    try:
        with sr.Microphone(device_index=1, sample_rate=48000) as source:
            r.adjust_for_ambient_noise(source)
            printOver('listening...')
            # r.energy_threshold()
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
                entities = client.analyze_entities(document=document)
                sentimentScr = int(round((sentiment.score + 1) * (255 / 2)))
                sentimentMag = int(round((sentiment.magnitude + 1) * (255 / 2)))
                printOver('feeling...')
                print('\nSentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))
                print('SentimentScr: ' + str(sentimentScr))
                print('SentimentMag: ' + str(sentimentMag))
                print(entities)

                try:
                    # changeSentimentColor(sentiment, text)
                    createTkImage(sentiment)
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
hostcheck()
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(info['index'], info['name'])

while True:
    record()
