from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from django.db import connection
from django.core.paginator import Paginator


# Create your views here.

def error_500_view(request):
    print("Internal server error handler")
    return render(request, '500.html', status=500)


def error_404_view(request, exception):
    print("404 handler")
    return render(request, '404.html', status=404)


class HomePage(View):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class SearchByCritic(View):
    template_name = 'serach_by_critic.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class GenreChoice(View):
    template_name = 'genre_choice.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

# query 1- reviews by critics
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
            if not rows:
                return render(request, 'no_results.html', {"phrase": critic_name})
        return render(request, self.template_name, {"reviews_list": rows, "critic": critic_name})


# query 2- users rating
class PopularMoviesUsers(ListView):
    template_name = 'movies_by_users_rating.html'
    query = "SELECT Movie.title, Movie.vote_avg, summary, link FROM Review JOIN Movie ON Movie.ID = Review.movie_id" \
            " order by Movie.vote_avg desc"

    def get(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute(self.query)
            rows = cursor.fetchall()
            if not rows:
                return render(request, 'no_results.html', {"phrase": "Popular movies"})
        length = len(rows)
        paginator = Paginator(rows, 20)
        page = request.GET.get('page')

        rows = paginator.get_page(page)
        return render(request, self.template_name, {"reviews_list": rows, "total_amount": length})


# query 3- critics picks
class PopularMoviesCritics(ListView):
    template_name = 'movies_by_critics_picks.html'
    query = "SELECT Movie.title AS Movie_title, summary, link FROM Review JOIN Movie ON Movie.ID = Review.movie_id" \
            " WHERE critics_pick=1"

    def get(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute(self.query)
            rows = cursor.fetchall()
            if not rows:
                return render(request, 'no_results.html', {"phrase": "Critics picks"})
        return render(request, self.template_name, {"reviews_list": rows})


# query 4- full text, similar phrase
class KeyWordReview(ListView):
    template_name = 'movies_by_term.html'
    query = "SELECT Movie.title AS Movie_title, summary, link FROM Review JOIN Movie ON Movie.ID = Review.movie_id" \
            " WHERE MATCH(summary, headline) against (%s IN NATURAL LANGUAGE MODE) "

    def get(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            term = request.GET.get("phrase", "")
            cursor.execute(self.query, (term,))
            rows = cursor.fetchall()
            if not rows:
                return render(request, 'no_results.html', {"phrase": term})
        return render(request, self.template_name, {"reviews_list": rows, "phrase": term})


# query 5- pick statistics by critic
class MoviesPicked(ListView):
    template_name = 'movies_picked_by_critic.html'
    query = "SELECT Person.name, count(*), SUM(critics_pick) from Person join Review on Person.ID = Review.critic_id" \
            " where Person.name=%s group by critic_id "

    def get(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            critic = kwargs['critic']
            cursor.execute(self.query, (critic,))
            row = cursor.fetchone()
            if not row:
                return render(request, 'no_results.html', {"phrase": critic})
        return render(request, self.template_name, {"critic_name": row[0], "count": row[2], "total": row[1]})


# query 6 picks by genres
class MoviesPickedGenre(ListView):
    template_name = 'movies_by_genre.html'
    query = "SELECT Movie.title AS Movie_title, summary, link FROM Review JOIN Movie ON Movie.ID = Review.movie_id " \
            "JOIN Genre on Genre.ID = Movie.category_id WHERE critics_pick = 1 AND category_name=%s"

    def get(self, request, *args, **kwargs):
        category_name = kwargs["genre"]
        with connection.cursor() as cursor:
            cursor.execute(self.query, (category_name,))
            rows = cursor.fetchall()
            if not rows:
                return render(request, 'no_results.html', {"phrase": category_name})
        return render(request, self.template_name, {"reviews_list": rows})


# query 7 user score by genre
class GenreUsersStats(ListView):
    template_name = 'user_stats.html'
    query = "SELECT AVG(Movie.vote_avg) as vote, AVG(Movie.vote_count), category_name FROM Movie join Genre ON Movie.category_id = Genre.ID group by Movie.category_id order by vote  desc"

    def get(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute(self.query)
            rows = cursor.fetchall()
            if not rows:
                return render(request, 'no_results.html', {"phrase": "User stats"})
        return render(request, self.template_name, {"reviews_list": rows})
