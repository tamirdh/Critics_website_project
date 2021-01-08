from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomePage.as_view(), name='finder_home'),
    path('critic=<str:critic>/', views.ReviewsByCritic.as_view()),
    path('popular/', views.PopularMoviesUsers.as_view(), name='finder_popular'),
    path('critic-pick/', views.PopularMoviesCritics.as_view()),
    path('phrase=<str:phrase>/', views.KeyWordReview.as_view())
]
