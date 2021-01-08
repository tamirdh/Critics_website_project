from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from django.db import connection


# Create your views here.
class HomePage(View):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


# query 1
class ReviewsByCritic(ListView):
    template_name = 'reviews_by_critic.html'
    query = "select Movie.title as Movie_title, Person.name as critic, summary, link from Person join Review on" \
            " Person.ID = Review.critic_id join Movie on Movie.ID = Review.movie_id WHERE Person.name LIKE %s"

    def get(self, request, *args, **kwargs):
        critic_name = kwargs["critic"]
        with connection.cursor() as cursor:
            new_critic_name = "%{}%".format(critic_name)
            cursor.execute(self.query, (new_critic_name,))
            rows = cursor.fetchall()
        return render(request, self.template_name, {"reviews_list": rows, "critic": critic_name})


# query 2
class PopularMoviesUsers(ListView):
    template_name = 'movies_by_users_rating.html'
    query = "SELECT Movie.title, Movie.vote_avg, summary, link FROM Review JOIN Movie ON Movie.ID = Review.movie_id" \
            " order by Movie.vote_avg desc;"

    def get(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute(self.query)
            rows = cursor.fetchall()
        return render(request, self.template_name, {"reviews_list": rows})


# query 3
class PopularMoviesCritics(ListView):
    template_name = 'movies_by_critics_picks.html'
    query = "SELECT Movie.title AS Movie_title, summary, link FROM Review JOIN Movie ON Movie.ID = Review.movie_id" \
            " WHERE critics_pick=1"

    def get(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute(self.query)
            rows = cursor.fetchall()
        return render(request, self.template_name, {"reviews_list": rows})


# query 4- full text
class KeyWordReview(ListView):
    template_name = 'movies_by_term.html'
    query = "SELECT Movie.title AS Movie_title, summary, link FROM Review JOIN Movie ON Movie.ID = Review.movie_id" \
            " WHERE MATCH(summary, headline) against (%s IN NATURAL LANGUAGE MODE) "

    def get(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            term = kwargs['phrase']
            cursor.execute(self.query, (term,))
            rows = cursor.fetchall()
        return render(request, self.template_name, {"reviews_list": rows, "phrase": term})
