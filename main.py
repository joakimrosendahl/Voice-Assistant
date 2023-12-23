import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os
import time
import speech_recognition as sr
import pyttsx3
import pyaudio
import pytz 
import subprocess

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
MONTHS = ["january", "febuary", "march", "april", "may", "june", "july", "august", "september", "october",
          "november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"] 
DAY_EXTENTIONS =["rd", "th", "st", "nd"]


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
        except Exception as e:
            print("Ecxeption: " + str(e))
        
    return said.lower()

# vet inte varför men utan att kalla på speak såhär så får jag en massa konstiga meddelanden om ALSA i terminalen, 
# men det är inte några varningar eller error medelanden utan bara skare jag inte förstår mig på.
# speak("What can I do for you?") men hände inte längre när jag tog bort if "hello" in adio_text koden



def authenticate_google():
  """Shows basic usage of the Google Calendar API.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "client_secret_1044186763148-eqdr1fdcr6lo3pgcgdqlkhsjn47lr1ln.apps.googleusercontent.com.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

  except HttpError as error:
    print(f"An error occurred: {error}")

  return service

def get_events(day, service):
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)
    

    events_result = (
        service.events().list(
           # min studie kallender, Kan jag ge den åtkomst till alla med en lije kod eller måste jag göra samma för alla?
            calendarId="55k18cm5jng81dh84155fifo58@group.calendar.google.com",
            timeMin = date.isoformat(),
            timeMax = end_date.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    

    if not events:
      speak("No upcoming events found.")
    else:
      speak(f"You have {len(events)} events on this day.")

    # Prints the start and name of the next n events
      for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        start_time = str(start.split("T")[1].split("-")[0])
        
        print(event["summary"] + " at " + start_time)

def get_date(text):
   text = text
   today = datetime.date.today()

   if text.count("today") > 8:
      return today
   
   day = -1
   day_of_week = -1
   month = -1
   year = today.year

   for word in text.split():
      if word in MONTHS:
         month = MONTHS.index(word) + 1
      elif word in DAYS:
         day_of_week = DAYS.index(word)
      elif word.isdigit():
         day = int(word)
      else:
         for ext in DAY_EXTENTIONS:
            found = word.find(ext)
            if found > 0:
               try:
                  day = int(word[:found])
               except:
                  pass
   if month < today.month and month != -1:
      year = year + 1

   if day < today.day and month == -1 and day != -1:
      month = month + 1

   if month == -1 and day == -1 and day_of_week != -1:
      current_day_of_week = today.weekday()
      dif = day_of_week - current_day_of_week

      if dif < 0:
         dif += 7
         if text.count("next") >= 1:
            dif += 7

      return today + datetime.timedelta(dif)
   if month == -1 or day == -1:
      return None
   return datetime.date(month = month, day = day, year = year)


   
def studying_math():
   date = datetime.datetime.now()
   file_name = str(date).replace(":", "-" + "-note.txt")
   
  
   url = "file:///home/joakim/Downloads/pdfcoffee.com_book-contemporary-linear-algebra-by-howard-anton-robert-c-busby-3-pdf-free.pdf"
   subprocess.Popen(["google-chrome", url])
   print("Math iniciated")

def studying_programming():
   print("programming")

def studying_ICS():
   print("ICS")

def resting():
   print("rest")

def recipe():
   print("recipe")

def meal():
   print("meal")


SERVICE = authenticate_google()
print("Start")
text = get_audio()

CALENDAR_LIST = ["what do i have", "do i have plans", "am i busy"]
for phrase in CALENDAR_LIST:
   if phrase in text:
      date = get_date(text)
      if date:
        get_events(date, SERVICE)
      else:
         speak("Pleas try again")

INITIATE_SESSION = {
   "math": studying_math, 
   "programming": studying_programming,
   "i can study": studying_ICS,
   "rest": resting,
   "recipe": recipe,
   "meal": meal
   
}

SESSION_CALLS = ["math", "programming", "i can study"]
for phrase in SESSION_CALLS:
   if "initiate" in text and phrase in text:
      INITIATE_SESSION[phrase]()
      # starta timer
      # fil för organisation och sparande av data.
      # terminate session
