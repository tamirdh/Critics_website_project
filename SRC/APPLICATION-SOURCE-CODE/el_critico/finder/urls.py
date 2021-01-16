from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomePage.as_view(), name='finder_home'),
    path('critic/', views.SearchByCritic.as_view(), name="critic_search"),
    path('critic/<str:critic>/', views.ReviewsByCritic.as_view(), name="critic_revs"),  # search by critic name
    path('popular/', views.PopularMoviesUsers.as_view(), name='finder_popular'),
    path('critic-pick/', views.PopularMoviesCritics.as_view(), name='finder_critics'),
    path('context/<str:phrase>/', views.KeyWordReview.as_view(), name='finder_phrase'),    # search by given phrase (context)
    path('critic-pick/filter/<str:critic>/', views.MoviesPicked.as_view(), name="critic_stats"),  # search stats by critic name
    path('genere-stats/', views.GenreChoice.as_view(), name="genre_choice"),
    path('genre-stats/category/<str:genre>', views.MoviesPickedGenre.as_view(), name="genre_stats"),    # search stats by genere
    path('stats/users', views.GenreUsersStats.as_view(), name='finder_users'),
    path('stats/actor', views.ActorStats.as_view()),
    path('stats/director', views.DirectorReviews.as_view())

]
