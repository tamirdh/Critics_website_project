from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomePage.as_view(), name='finder_home'),
    path('critic/', views.SearchByCritic.as_view(), name="critic_search"),
    path('critic/<str:critic>/', views.ReviewsByCritic.as_view(), name="critic_revs"),  # search by critic name
    path('popular/', views.PopularMoviesUsers.as_view(), name='finder_popular'),
    path('critic-pick/', views.PopularMoviesCritics.as_view(), name='finder_critics'),
    path('context/', views.KeyWordReview.as_view(), name='finder_phrase'),    # search by given phrase (context)
    path('critic-pick/filter/<str:critic>/', views.MoviesPicked.as_view(), name="critic_stats"),  # search stats by critic name
    path('critic-pick/filter/genre/<str:genre>', views.MoviesPickedGenre.as_view()),    # search stats by genere
    path('stats/users', views.GenreUsersStats.as_view(), name='finder_users')
]
