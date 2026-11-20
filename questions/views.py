from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.csrf import csrf_failure as default_csrf_failure

from .forms import AnswerForm, CorrectAnswerForm, QuestionForm, VoteForm
from .models import Answer, Question, Tag
from .pagination import paginate
from .shortcuts import render_with_popular_tags

ANSWERS_PER_PAGE = 5


def render_list(request, template, questions, heading, **context):
    page = paginate(questions, request)
    return render_with_popular_tags(request, template, page_obj=page, heading=heading, **context)


def index(request):
    return render_list(
        request, 'questions/index.html', Question.objects.newest(request.user), 'Новые вопросы',
    )


def hot(request):
    return render_list(
        request, 'questions/hot.html', Question.objects.best(request.user), 'Горячие вопросики',
    )


def tag(request, tag):
    active_tag = get_object_or_404(Tag, slug=tag)
    return render_list(
        request, 'questions/tag.html', Question.objects.by_tag(active_tag, request.user),
        f'Вопросы по тегу: {active_tag.name}', active_tag=active_tag,
    )


def question(request, question_id):
    if request.method == 'POST':
        return add_answer(request, question_id)
    question = get_object_or_404(Question.objects.for_display(request.user), pk=question_id)
    return render_question(request, question, AnswerForm())


def render_question(request, question, form):
    page = paginate(Answer.objects.for_question(question, request.user), request, per_page=ANSWERS_PER_PAGE)
    return render_with_popular_tags(
        request, 'questions/question.html', question=question, page_obj=page, form=form,
    )


@login_required
def add_answer(request, question_id):
    question = get_object_or_404(Question.objects.for_display(request.user), pk=question_id)
    form = AnswerForm(request.POST)
    if not form.is_valid():
        return render_question(request, question, form)
    answer = form.save(author=request.user, question=question)
    preceding = question.answers.filter(
        Q(is_correct=True) | Q(created_at__lt=answer.created_at)
        | Q(created_at=answer.created_at, pk__lt=answer.pk),
    ).count()
    page = preceding // ANSWERS_PER_PAGE + 1
    return redirect(f'{question.get_absolute_url()}?page={page}#answer-{answer.pk}')


@login_required
def ask(request):
    form = QuestionForm(request.POST if request.method == 'POST' else None)
    if form.is_valid():
        return redirect(form.save(author=request.user))
    return render_with_popular_tags(request, 'questions/ask.html', form=form)


def csrf_failure(request, reason=''):
    if request.resolver_match and request.resolver_match.url_name in {
        'question_vote', 'answer_vote', 'correct_answer',
    }:
        return JsonResponse({'error': 'Ошибка CSRF. Обновите страницу.'}, status=403)
    return default_csrf_failure(request, reason=reason)


@transaction.atomic
def ajax_submit(request, form_class, **kwargs):
    if request.method != 'POST':
        response = JsonResponse({'error': 'Используйте метод POST.'}, status=405)
        response['Allow'] = 'POST'
        return response
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Войдите, чтобы выполнить это действие.'}, status=401)
    form = form_class(request.POST, user=request.user, **kwargs)
    if form.is_valid():
        return JsonResponse(form.save())
    errors = [error for field_errors in form.errors.as_data().values() for error in field_errors]
    status = {'forbidden': 403, 'duplicate': 409}.get(errors[0].code, 400)
    return JsonResponse({'error': ' '.join(message for error in errors for message in error)}, status=status)


def vote(request, model):
    return ajax_submit(request, VoteForm, model=model)


def correct_answer(request):
    return ajax_submit(request, CorrectAnswerForm)
