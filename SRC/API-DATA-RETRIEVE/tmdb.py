import requests
import json


class tmdbApi:
    def __init__(self):
        with open("api_creds.json") as cred_source:
            data = json.load(cred_source)
            self.token = data["tmdb"]["token"]
            self.base_url = data["tmdb"]["base url"]
            self.headers = {"Authorization": "Bearer {}".format(self.token)}

    def get_movie_genres(self):
        url_suffix = "/genre/movie/list"
        resp = requests.get(url=self.base_url + url_suffix, headers=self.headers)
        if resp.ok:
            data = resp.json()
            return data["genres"]
        else:
            print("Movie genres listing failed with {}".format(resp.content))

    def get_movie_top_rated(self):
        url_suffix = "/movie/top_rated"
        resp = requests.get(self.base_url + url_suffix, headers=self.headers)
        if resp.ok:
            data = resp.json()
            return data["results"]
        else:
            print("Movies top rated listing failed with {}".format(resp.content))

    def get_movie_popular(self, page=1):
        url_suffix = "/movie/popular"
        resp = requests.get(self.base_url + url_suffix, headers=self.headers, params={"page":page})
        if resp.ok:
            data = resp.json()
            return data["results"]
        else:
            print("Movies top rated listing failed with {}".format(resp.content))

    def get_movie_credits(self, tmdb_id):
        url_suffix = "/movie/{movie_id}/credits".format(movie_id=tmdb_id)
        resp = requests.get(self.base_url + url_suffix, headers=self.headers)
        if resp.ok:
            data = resp.json()
            return data
        else:
            print("Movie credits listing failed with {}".format(resp.content))

    def get_person(self, tmdb_person_id):
        url_suffix = "/person/{person_id}".format(person_id=tmdb_person_id)
        resp = requests.get(self.base_url + url_suffix, headers=self.headers)
        if resp.ok:
            data = resp.json()
            return data
        else:
            print("Get person failed with {}".format(resp.content))

    def get_movie_by_id(self, movie_id):
        url_suffix = "/movie/{movie_id}".format(movie_id=movie_id)
        resp = requests.get(self.base_url + url_suffix, headers=self.headers)
        if resp.ok:
            data = resp.json()
            return data
        else:
            print("Get movie details failed with {}".format(resp.content))



