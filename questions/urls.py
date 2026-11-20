from django.urls import path

from . import views
from .models import Answer, Question

app_name = 'questions'

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<slug:tag>/', views.tag, name='tag'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('ask/', views.ask, name='ask'),
    path('ajax/question/vote/', views.vote, {'model': Question}, name='question_vote'),
    path('ajax/answer/vote/', views.vote, {'model': Answer}, name='answer_vote'),
    path('ajax/answer/correct/', views.correct_answer, name='correct_answer'),
]
