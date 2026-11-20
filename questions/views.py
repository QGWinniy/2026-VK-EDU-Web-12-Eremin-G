from django.shortcuts import get_object_or_404

from .models import Answer, Question, Tag
from .pagination import paginate
from .shortcuts import render_with_popular_tags


def render_list(request, template, questions, heading, **context):
    page = paginate(questions, request)
    return render_with_popular_tags(request, template, page_obj=page, heading=heading, **context)


def index(request):
    return render_list(
        request, 'questions/index.html', Question.objects.newest(), 'Новые вопросы',
    )


def hot(request):
    return render_list(
        request, 'questions/hot.html', Question.objects.best(), 'Горячие вопросики',
    )


def tag(request, tag):
    active_tag = get_object_or_404(Tag, slug=tag)
    return render_list(
        request, 'questions/tag.html', Question.objects.by_tag(active_tag),
        f'Вопросы по тегу: {active_tag.name}', active_tag=active_tag,
    )


def question(request, question_id):
    question = get_object_or_404(Question.objects.for_display(), pk=question_id)
    page = paginate(Answer.objects.for_question(question), request, per_page=5)
    return render_with_popular_tags(request, 'questions/question.html', question=question, page_obj=page)


def ask(request):
    return render_with_popular_tags(request, 'questions/ask.html')
