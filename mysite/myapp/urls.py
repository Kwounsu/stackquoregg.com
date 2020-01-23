from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index),
    path('suggestions/', views.suggestions_view),
    path('suggestion/', views.suggestion_form_view),
    path('answer/<int:instance_id>/', views.comments_view),
    path('answer/<int:instance_id>/<int:delete>/', views.comments_view),
    path('tutorForm/', views.tutor_form_view),
    path('login/', auth_views.LoginView.as_view()),
    path('logout/', views.logout_view),
    path('register/', views.register),
    path('about/', views.about),
    path('qna/', views.qna),
    path('qna/<int:page>/', views.qna),
    path('tutor/', views.tutor),
    path('tutor/<int:page>/', views.tutor),
    path('tutor/<int:page>/<int:delete>/', views.tutor),
    path('upvote/<int:comm_id>/', views.upvote),
    path('search/', views.search, name='search'),
    path('searchTutor/', views.searchTutor, name='searchTutor'),
    path('tutor_chat/<slug:room>/', views.chatting),
    path('conversation/', views.broadcast),
    path('conversations/', views.conversations),
    path('conversations/<slug:id>/delivered/', views.delivered),
]