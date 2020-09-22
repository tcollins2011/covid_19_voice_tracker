import requests
import json

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
        self.get_data()

    def get_data(self):
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/last_ready_run/data', params={"api_key" : API_KEY})
        self.data = json.loads(response.text)

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

data = Data(API_KEY, PROJECT_TOKEN)


