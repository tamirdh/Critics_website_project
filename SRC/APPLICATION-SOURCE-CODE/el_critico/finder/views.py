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


class SearchByPerson(View):
    template_name = 'search_by_person.html'

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

        paginator = Paginator(rows, 20)
        page = request.GET.get('page')
        rows = paginator.get_page(page)

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

        paginator = Paginator(rows, 20)
        page = request.GET.get('page')
        rows = paginator.get_page(page)

        return render(request, self.template_name, {"reviews_list": rows})


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

        paginator = Paginator(rows, 20)
        page = request.GET.get('page')
        rows = paginator.get_page(page)

        return render(request, self.template_name, {"reviews_list": rows})


# query 4- full text, similar phrase
class KeyWordReview(ListView):
    template_name = 'movies_by_term.html'
    query = "SELECT Movie.title AS Movie_title, summary, link FROM Review JOIN Movie ON Movie.ID = Review.movie_id" \
            " WHERE MATCH(summary, headline) against (%s IN NATURAL LANGUAGE MODE) "

    def get(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            term = kwargs['phrase']
            cursor.execute(self.query, (term,))
            rows = cursor.fetchall()
            if not rows:
                return render(request, 'no_results.html', {"phrase": term})

        paginator = Paginator(rows, 20)
        page = request.GET.get('page')
        rows = paginator.get_page(page)

        return render(request, self.template_name, {"reviews_list": rows, "phrase": term})


# query 5- pick statistics by critic
class MoviesPicked(ListView):
    template_name = 'movies_picked_by_critic.html'
    query = "SELECT name, amount, picks, bio, image from ( SELECT Person.name, COUNT(*) as amount, SUM(critics_pick)" \
            " as picks, Person.ID FROM Person JOIN Review ON Person.ID = Review.critic_id JOIN Critic ON Critic.ID" \
            " = Person.ID WHERE Person.name = %s GROUP BY critic_id) as T JOIN Critic on T.ID = Critic.ID"

    def get(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            critic = kwargs['critic']
            cursor.execute(self.query, (critic,))
            row = cursor.fetchone()
            if not row:
                return render(request, 'no_results.html', {"phrase": critic})
        return render(request, self.template_name,
                      {"critic_name": row[0], "count": row[2], "total": row[1], "bio": row[3], "image": row[4]})


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
        paginator = Paginator(rows, 20)
        page = request.GET.get('page')
        rows = paginator.get_page(page)
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


# query 8 actor reviews
class ActorStats(ListView):
    template_name = "actor_reviews.html"
    query = "SELECT Person.name, Movie.title, Review.link, Review.summary, Actor.popularity FROM Review JOIN Movie on Movie.ID = Review.movie_id JOIN Appearances on Movie.ID = Appearances.movie_id JOIN Actor on Appearances.actor_id = Actor.ID Join Person on Person.ID = Actor.ID WHERE Person.name LIKE %s ORDER BY Actor.popularity DESC"

    def get(self, request, *args, **kwargs):
        actor_name = kwargs["actor"]
        with connection.cursor() as cursor:
            new_actor_name = "%{}%".format(actor_name)
            cursor.execute(self.query, (new_actor_name,))
            rows = cursor.fetchall()
            if not rows:
                return render(request, 'no_results.html', {"reviews_list": rows ,"phrase": actor_name})

        paginator = Paginator(rows, 20)
        page = request.GET.get('page')
        rows = paginator.get_page(page)
        return render(request, self.template_name, {"reviews_list": rows, "actor": actor_name})


# query 9 director reviews
class DirectorReviews(ListView):
    template_name = "director_reviews.html"
    query = "SELECT Person.name, Director.birthday, Director.bio, Movie.title, Review.link, Review.summary from Director JOIN Movie on Movie.director_id = Director.ID Join Review on Movie.ID = Review.movie_id Join Person on Person.ID = Director.ID WHERE Person.name LIKE %s"

    def get(self, request, *args, **kwargs):
        director_name = kwargs["director"]
        with connection.cursor() as cursor:
            new_director_name = "%{}%".format(director_name)
            cursor.execute(self.query, (new_director_name,))
            rows = cursor.fetchall()
            if not rows:
                return render(request, 'no_results.html', {"reviews_list": rows ,"phrase": director_name})

        paginator = Paginator(rows, 20)
        page = request.GET.get('page')
        rows = paginator.get_page(page)
        return render(request, self.template_name, {"reviews_list": rows, "director": director_name})
