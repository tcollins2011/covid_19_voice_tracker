import requests
import json
import pyttsx3
import re
import speech_recognition as sr
import threading 
import time


API_KEY = 'tDLjW0sFmB5X'
PROJECT_TOKEN = 'tz1ObDDHpiZm'
RUN_TOKEN = 'tHzKTFJnAurr'

class Data:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = { 
            "api_key": self.api_key
        }
        self.data = self.get_data()

    def get_data(self):
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data', params=self.params)
        data = json.loads(response.text)
        return data

    def get_total_cases(self):
        data = self.data['total']

        for evidence in data:
            if evidence['name']  == "Coronavirus Cases:":
                return evidence['value']
    
    def get_total_deaths(self):
        data = self.data['total']

        for evidence in data:
            if evidence['name']  == "Deaths:":
                return evidence['value']

    def get_country_data(self,country):
        data = self.data['Country']

        for evidence in data:
            if evidence['name'].lower() == country.lower():
                return evidence
        
        return "0"

    def get_list_of_countires(self):
        countries = []
        for country in self.data['Country']:
            countries.append(country['name'].lower())

        return countries

    def update_data(self):
        response = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run', params = self.params)

        def poll():
            time.sleep(0.1)
            old_data = self.data
            while True:
                new_data = self.get_data()
                if new_data != old_data:
                    self.data = new_data
                    print('Data Updated')
                    break
                time.sleep(5)


        t = threading.Thread(target=poll)
        t.start()
        

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ''

        try: 
            said = r.recognize_google(audio)
        except Exception as e:
            print ("Exception:", str(e))

    return said.lower()




def main():
    print("Started Program")
    data = Data(API_KEY, PROJECT_TOKEN) 
    END_PHRASE = 'stop'
    country_list = data.get_list_of_countires()

    def data_exists(country,type):
        
        if type in data.get_country_data(country):
            return data.get_country_data(country)[type]
               
        else:
            return 'no data for this request'
             
    TOTAL_PATTERNS = { 
        re.compile("[\w\s]+ total [\w\s]+ cases"): data.get_total_cases,
        re.compile("[\w\s]+ total cases"): data.get_total_cases,
        re.compile("total cases"): data.get_total_cases,
        re.compile("[\w\s]+ total [\w\s]+ deaths"): data.get_total_deaths,
        re.compile("[\w\s]+ total deaths"): data.get_total_deaths,
        re.compile("total deaths"): data.get_total_deaths,  
    }

    COUNTRY_PATTERNS = {
        re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data_exists(country, 'total_cases'),
        re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data_exists(country, 'total_deaths'),
        re.compile("[\w\s]+ new [\w\s]+"): lambda country: data_exists(country, 'New_Cases'),
        re.compile("[\w\s]+ tests per million [\w\s]+"): lambda country: data_exists(country, 'total_cases_per1M_pop'),
        re.compile("[\w\s]+ cases per million [\w\s]+"): lambda country: data_exists(country, 'deaths_per1m_pop'),
        re.compile("[\w\s]+ deaths per million [\w\s]+"): lambda country: data_exists(country, 'tests_per1M_pop'),
        re.compile("[\w\s]+ active cases[\w\s]+"): lambda country: data_exists(country, 'active_cases'),
      
    }

    UPDATE_COMMAND = 'update'
    while True:
        print("Listening...")

        text = get_audio()
        print(text)
        result = None

        for pattern, func in TOTAL_PATTERNS.items():
            if pattern.match(text):
                result = func()
                break

        for pattern, func in COUNTRY_PATTERNS.items():
            if pattern.match(text):
                words = set(text.split(" "))
                for country in country_list:
                    if country in words:
                        result = func(country)
                        break


        if text == UPDATE_COMMAND:
            result = 'Data is being updated. This may take a moment!'
            data.update_data()

        if result:
            speak(result)
    
        if text.find(END_PHRASE) != -1:
            print('Ended Program')
            break

main()