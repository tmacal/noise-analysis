import os
import sys
import time
import serial.threaded
import datetime
import speech_recognition as sr
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

## INITIALISE OBJECTS ##
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\Tad\\Desktop\\TargetedAdvertising-dc956f1a9b6b.json"
timestr = time.strftime("%Y%m%d-%H%M%S")
endTime = datetime.datetime.now() + datetime.timedelta(minutes=1)
ser = serial.Serial(
    port='COM11',
    baudrate=115200,
)


## HELPER METHODS / OBJECTS ##
def printOver(str):
    sys.stdout.write("\r" + (str))
    sys.stdout.flush()


## OUTPUT FUCNTIONS ##
def serialPipe(sentiment, text):

    #drawHappy
    if 0.25 <= sentiment.score <= 1.0:
        print("\nGood: {}".format(text))
        ser.write("happy".encode('utf-8'))

    # drawSad
    if -1.0 <= sentiment.score <= -0.25:
        print("\nBad: {}".format(text))
        ser.write("sad".encode('utf-8'))

    # drawNeutral
    if -0.25 <= sentiment.score <= 0.25:
        print("\nNeutral: {}".format(text))
        ser.write("neutral".encode('utf-8'))


## MAIN FUNCTION ##
def record():
    r = sr.Recognizer()
    try:
        with sr.Microphone(device_index=1, sample_rate=48000) as source:
            printOver('adjusting for ambient noise...')
            r.adjust_for_ambient_noise(source)
            printOver('listening...')
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
                printOver('feeling...')
                with open("Speech2mood_log" + timestr + ".txt", "a") as text_file:
                    text_file.write(timestr + 'Res: ' + str(document) + str(entities))
                    text_file.write('\nSentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))

                try:
                    serialPipe(sentiment, text)
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


## SYSTEM / INPUT DEVICES CHECK ##
ser.close()
ser.open()
while True:
    record()
    if datetime.datetime.now() >= endTime:
        continue
