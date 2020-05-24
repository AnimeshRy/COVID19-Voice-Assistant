import pyttsx3
import speech_recognition as sr
import re
from DataClass import Data

"""Voice assistent for the number of deaths and total cases of coronavirus worlwide using parsehub scraping api"""

API_KEY = "{API-Key}"
PROJECT_TOKEN = "{Project-Token}"
RUN_TOKEN = "{Run-Token}"


def main():
    print("Started Program")
    data = Data(API_KEY, PROJECT_TOKEN)
    country_list = data.get_list_of_countries()

    TOTAL_PATTERNS = {
        re.compile("[\w\s]+ total [\w\s]+ cases"): data.get_total_cases,
        re.compile("[\w\s]+ total cases"): data.get_total_cases,
        re.compile("[\w\s]+ total [\w\s]+ death|deaths"): data.get_total_deaths,
        re.compile("[\w\s]+ total death|deaths"): data.get_total_deaths
    }

    COUNTRY_PATTERNS = {
        re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)['total_cases'],
        re.compile("[\w\s]+ new death|deaths [\w\s]+"): lambda country: data.get_country_data(country)['new_deaths'] if (data.get_country_data(country)['new_deaths'] != "") else data.get_country_data(country)['total_deaths'],
        re.compile("[\w\s]+ death|deaths [\w\s]+"): lambda country: data.get_country_data(country)['total_deaths'],
    }

    UPDATE_COMMAND = "update"
    END_PHRASE = "stop"

    while True:
        print("Listening...")
        text = get_audio()
        print(text)
        result = None

        for pattern, func in COUNTRY_PATTERNS.items():
            if pattern.match(text):
                words = set(text.split(" "))
                for country in country_list:
                    if country in words:
                        result = func(country)
                        break

        for pattern, func in TOTAL_PATTERNS.items():
            if pattern.match(text):
                result = func()
                break

        if text == UPDATE_COMMAND:
            result = "Data is being updated. This may take a moment!"
            data.update_data()

        if result:
            print(result)
            speak(result)

        if text.find(END_PHRASE) != -1:  # stop loop
            print("Exiting...", end="")
            break


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
        except Exception as e:
            print("Exception:", str(e))

    return said.lower()


if __name__ == "__main__":
    main()
