import requests
import json
import time

class nyApi:
    def __init__(self):
        with open("api_creds.json") as cred_source:
            data = json.load(cred_source)
            self.key = data["new_york_times"]["key"]
            self.base_url = data["new_york_times"]["base url"]

    def get_all_critics(self):
        time.sleep(6)
        url_suffix = "/critics/{reviewer}.json".format(reviewer="all")
        params = {"api-key": self.key}
        critics = list()
        resp = requests.get(self.base_url + url_suffix, params)
        if resp.ok:
            data = resp.json()
            for critic in data["results"]:
                critics.append(critic)
            return critics
        else:
            print("Get all critics failed with: {}".format(resp.content))
            raise ValueError("API value error")

    def get_all_reviews(self, offset=0):
        time.sleep(6)
        url_suffix = "/reviews/all.json"
        params = {"api-key": self.key, "offset": offset}
        resp = requests.get(self.base_url + url_suffix, params=params)
        if resp.ok:
            return resp.json()["results"]
        else:
            print("Getting all reviews failed, {}".format(resp.content))
            raise ValueError("API value error")

