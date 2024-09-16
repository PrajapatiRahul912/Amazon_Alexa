import os
import webbrowser
import datetime
import requests
import pyttsx3
import speech_recognition as sr
import threading
import wikipedia
from firebase_admin import firestore
from db import connectDb

connectDb()
db = firestore.client()

def say(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen_for_wake_phrase():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.energy_threshold = 1300
        r.pause_threshold = 0.6
        print("Listening for wake phrase...")
        audio = r.listen(source)
        try:
            print("Recognizing....")
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            if "hey route" in query.lower():
                print("Hello boss")
                say("Hello boss")
                return query[len("hey route"):].strip()
        except Exception as e:
            print(e)
            return None

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.energy_threshold = 1300
        r.pause_threshold = 0.6
        print("Listening...")
        audio = r.listen(source)
        try:
            print("Recognizing....")
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query.lower()
        except Exception as e:
            print(e)
            return "Sorry, I couldn't understand. Please try again."

def open_website(query):
    sites = {
        "youtube": "https://www.youtube.com",
        "wikipedia": "https://www.wikipedia.com",
        "google": "https://www.google.com",
        "Khan Academy": "https://www.khanacademy.org",
        "Coursera": "https://www.coursera.org",
        "edX": "https://www.edx.org",
        "Udemy": "https://www.udemy.com",
        "Udacity": "https://www.udacity.com",
        "Codecademy": "https://www.codecademy.com",
        "freeCodeCamp": "https://www.freecodecamp.org",
        "W3Schools": "https://www.w3schools.com",
        "MDN Web Docs": "https://developer.mozilla.org",
        "Stack Overflow": "https://stackoverflow.com",
        "GeeksforGeeks": "https://www.geeksforgeeks.org",
        "LeetCode": "https://leetcode.com",
        "HackerRank": "https://www.hackerrank.com",
        "Codewars": "https://www.codewars.com",
        "CodeSignal": "https://codesignal.com",
        "TopCoder": "https://www.topcoder.com",
        "Coderbyte": "https://coderbyte.com",
        "Exercism": "https://exercism.io",
        "The Odin Project": "https://www.theodinproject.com",
        "Launch School": "https://launchschool.com",
        "MIT OpenCourseWare": "https://ocw.mit.edu",
        "Stanford Online": "https://online.stanford.edu",
        "Harvard Online": "https://online-learning.harvard.edu",
        "MIT Scratch": "https://scratch.mit.edu",
        "ScratchEd": "https://scratch.mit.edu/educators",
        "ScratchJr": "https://www.scratchjr.org",
        "Code.org": "https://code.org",
        "MIT App Inventor": "http://appinventor.mit.edu",
        "Code Combat": "https://codecombat.com",
        "Code HS": "https://codehs.com",
        "Pluralsight": "https://www.pluralsight.com",
        "LinkedIn Learning": "https://www.linkedin.com/learning",
        "Skillshare": "https://www.skillshare.com",
        "Treehouse": "https://teamtreehouse.com",
        "Lynda": "https://www.lynda.com",
        "Codecademy": "https://www.codecademy.com",
        "chat": "https://chat.openai.com",
        "whatsapp": "https://www.whatsapp.com/"
    }
    for site, url in sites.items():
        if site in query:
            print(f"Opening {site}...")
            say(f"Opening {site}...")
            conv_doc_ref.add({"question": query, "answer": f"Opening {site}"})
            webbrowser.open(url)
            break

def get_weather(city):
    api_key = "92466df4635f85942552ab5441cee1da"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    if data["cod"] == 200:
        weather_description = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        say(f"The weather in {city} is {weather_description}. The temperature is {temperature} degrees Celsius.")
        print(weather_description)
        print(temperature)
        conv_doc_ref.add({"question": query, "answer": f"The weather in {city} is {weather_description}. The temperature is {temperature} degrees Celsius."})
    else:
        say("Sorry, I couldn't retrieve the weather information for that location.")

def search_wikipedia(query):
    try:
        # Set language (optional)
        wikipedia.set_lang("en")
        # Search Wikipedia
        result = wikipedia.summary(query, sentences=2)  # Get a summary of the search query
        return result
        conv_doc_ref.add({"question": query, "answer": result})
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Disambiguation Error: {e}"
    except wikipedia.exceptions.PageError as e:
        return f"Page Error: {e}"
    except Exception as e:
        return f"Error: {e}"

def set_reminder(query):
    try:
        # Extract the reminder message and time from the query
        if "to" not in query or "at" not in query:
            raise ValueError("Invalid reminder format. Please use 'Set reminder message to do at time.' format.")

        reminder_message = query.split("to")[1].split("at")[0].strip()
        reminder_time = query.split("at")[1].strip()

        # Save the reminder to Firebase
        doc_ref = db.collection("reminders").document()
        doc_ref.set({
            "message": reminder_message,
            "time": reminder_time
        })

        print(f"Reminder set: {reminder_message} at {reminder_time}")
        say(f"Reminder set: {reminder_message} at {reminder_time}")
        conv_doc_ref.add({"question": query, "answer": f"Reminder set: {reminder_message} at {reminder_time}"})
    except ValueError as e:
        print(f"Error setting reminder: {e}")
        say(f"Error setting reminder: {e}")


def get_reminders():
    reminders_ref = db.collection("reminders")
    reminders = reminders_ref.get()

    if not reminders:
        print("No reminders set.")
        say("No reminders set.")
        return

    for reminder in reminders:
        reminder_data = reminder.to_dict()
        reminder_message = reminder_data["message"]
        reminder_time = reminder_data["time"]
        print(f"Reminder: {reminder_message} at {reminder_time}")
        say(f"Reminder: {reminder_message} at {reminder_time}")
        conv_doc_ref.add({"question": query, "answer": f" Show Reminder: {reminder_message} at {reminder_time}"})

def delete_all_reminders():
    reminders_ref = db.collection("reminders")
    reminders = reminders_ref.get()

    for reminder in reminders:
        reminder.reference.delete()

    print("All reminders deleted.")
    say("All reminders deleted.")
    conv_doc_ref.add({"question": query, "answer": f"All reminders deleted"})

def open_google(que):
    # You can replace this search URL with any other method to get the video URL based on the video name
    search_url = f"https://www.google.com/search?q={que.replace(' ', '+')}"
    webbrowser.open(search_url)
    say("Opening in Google")
    conv_doc_ref.add({"question": que, "answer": f"{que} Searching on Google"})
def open_youtube_video(video_name):
    # You can replace this search URL with any other method to get the video URL based on the video name
    search_url = f"https://www.youtube.com/results?search_query={video_name.replace(' ', '+')}"
    webbrowser.open(search_url)
    say("Opening in Youtube")
    conv_doc_ref.add({"question": video_name, "answer": f"{video_name} Searching on youtube"})
def get_news():
    api_key = "9ed204430b2940158033661d4d3d371a"
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
    response = requests.get(url)
    data = response.json()

    if data["status"] == "ok":
        articles = data["articles"]
        count = 0
        for article in articles:
            if count >= 3:
                break
            title = article["title"]
            description = article["description"]
            print(f"Title: {title}")
            print(f"Description: {description}")
            print()
            say(title)
            count += 1
            conv_doc_ref.add({"question": query, "answer": f"Title: {title},Description: {description}"})
    else:
     print("Failed to fetch news.")


if __name__ == '__main__':

    conv_doc_ref = db.collection("conversation")
    while True:
        query = listen_for_wake_phrase()
        if query:
            query = query.lower()
            if "open" in query:
                threading.Thread(target=open_website, args=(query,)).start()
            elif "search" in query:
                result = search_wikipedia(query)
                print("Answer :", result)
                say(result)
                conv_doc_ref.add({"question": query, "answer": result})
            elif "play music" in query:
                musicPath = "E:/music.mp3"  # Change this path to your music file path
                print("Playing Music")
                say("Playing Music")
                os.system(f"start {musicPath}")
                conv_doc_ref.add({"question": query, "answer": "Playing music"})
            elif "time" in query:
                current_time = datetime.datetime.now().strftime("%H:%M:%S")
                print(f"Sir, the time is {current_time}")
                say(f"Sir, the time is {current_time}")
                conv_doc_ref.add({"question": query, "answer": current_time})
            elif "weather" in query:
                print("Sure, which city's weather would you like to know?")
                say("Sure, which city's weather would you like to know?")
                city = takeCommand()
                threading.Thread(target=get_weather, args=(city,)).start()
            elif "set a reminder" in query:
                set_reminder(query)
            elif "show reminders" in query:
                get_reminders()
            elif "delete all reminder" in query:
                delete_all_reminders()
            elif "news" in query or "current affairs" in query:
                get_news()
            elif "on youtube" in query:
                video_name = query
                open_youtube_video(video_name)
            elif "on google" in query:
                que = query
                open_google(que)
            elif "goodbye" in query:
                print("Goodbye boss, have a great day!")
                say("Goodbye boss, have a great day!")
                break
            else:
                say("Sorry, I didn't understand that command. Can you please repeat?")