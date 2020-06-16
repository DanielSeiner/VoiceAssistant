from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import time
import pyttsx3
import speech_recognition as sr
import pytz
import subprocess
import sys
import webbrowser
import commands

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
DAY_EXTENSIONS = ["nd", "rd", "th", "st"]

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_audio():
     r = sr.Recognizer()
     with sr.Microphone() as source:
         audio = r.listen(source)
         said = ""

         try:
             said = r.recognize_google(audio)
             print(said)
         except Exceotion as e:
            print("Exception: " + str(e))

     return said.lower()



#text = get_audio()

#if "hello" in text:
#    speak("hello, how are you?")

#if "what is your name" in text:
#    speak("My name is Edith")

#if "what does Edith mean" in text:
#    speak("Edith mean Even dead I'm the hero")




# If modifying these scopes, delete the file token.pickle.

def authenticate_google():

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service

def get_events(day, service):
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"You have{len(events)} events on this day.")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time= str(start.split("T")[1].split(":")[0])
            if int(start_time.split(":")[0]) < 12:
                start_time = start_time + "am"
            else:
                start_time = str(int(start_time.split(":")[0])-12) + start_time.split(":")[1]
                start_time = start_time + "pm"

            speak(event["summary"] + " at "+ start_time)

def get_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count==("today") > 0:
        return today

    day =-1
    day_of_week= -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month= MONTHS.index(word) + 1
        elif  word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENSIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass
    if month < today.month and month != -1:
        year = year+1

    if day < today.day and month == -1 and day != -1:
        month = month + 1

    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_the_week = today.weekday() #0-6
        dif = day_of_week - current_day_of_the_week

        if dif < 0:
            dif +=7
            if text.count("next") >= 1:
                dif+= 7
        return today + datetime.timedelta(dif)
    if month == -1 or day ==-1:
        return None
    return datetime.date(month=month, day = day, year = year)

def note(text):
    date = datetime.datetime.now()
    file_name = str(date).replace(":","-") + "-note.txt"
    with open(file_name, "w") as f:
        f.write(text)

    subprocess.Popen(["notepad.exe", file_name])
WAKE = "edith"
SHUT_DOWN = "close"
SERVICE = authenticate_google()

#ACTIONS (EDITH)
def open_web(url,name):
    print("Openning "+name+", sir.")
    speak("Openning "+name+", sir.")
    webbrowser.open(url)

def open_app(name,address):
    print("Openning app: "+name)
    speak("Openning app "+name+", sir.")
    os.startfile(address)

def open_folder(name):
    print("Openning folder "+name)
    speak("Openning folder "+name+", sir.")
    os.startfile(path)

print('Hello, to wake me up say "Edith"')
while True:
    print("I'm listening, sir.")
    text = get_audio()

    if text.count(WAKE) > 0:
        speak("Yes, sir.")
        text = get_audio()
    if SHUT_DOWN in text:
        sys.exit()
    CALENDAR_STRS = ["what do i have","do i have plans", "am i busy"]
    for phrase in CALENDAR_STRS:
        if phrase in text:
            date = get_date(text)
            if date:
                get_events(date, SERVICE)
            else:
                speak("I don't understand sir")

    NOTE_STRS = ["make a note","write this down","remember this","save this"]
    for phrase in NOTE_STRS:
        if phrase in text:
            speak("I'm listening, sir.")
            note_text = get_audio()
            note(note_text)
            speak("I save it to your personal storage.")

    END_STRS = ["turn off", "bye","take a rest","sleep"]
    for phrase in END_STRS:
        if phrase in text:
            speak("Goodbye, sir.")
            sys.exit()


    FOLDER_STRS = ['open a folder','show me main','workspace','show me folder']
    for phrase in FOLDER_STRS:
        if phrase in text:
            path="C:\\Users\\Dan\\OneDrive - SPŠ, Ústí nad Labem, Resslova 5, příspěvková organizace\\Voice Assistant"
            path=os.path.realpath(path)
            open_folder("Voice Assistant")


    GOOGLE_STRS = ["open chrome", "google chrome","open browser"]
    for phrase in GOOGLE_STRS:
        if phrase in text:
            open_app('google chrome',"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe")


    SPOTIFY_STRS = ["play music", "open spotify","spotify","show music"]
    for phrase in SPOTIFY_STRS:
        if phrase in text:
            open_web('https://www.spotify.com/ca-en/', 'spotify')

    YOUTUBE_STRS = ["show me youtube", "open youtube","youtube","play youtube"]
    for phrase in YOUTUBE_STRS:
        if phrase in text:
            open_web('https://www.youtube.com','youtube')

    BAKALARI_STRS = ["School", "open School","show School","show me school website"]
    for phrase in BAKALARI_STRS:
        if phrase in text:
            open_web('https://bakalari.skolnilogin.cz/next/dash.aspx','bakalari')

