from django.shortcuts import render

from .pagination import paginate


TAGS = ['python', 'django', 'web', 'sql', 'linux', 'html', 'css']
AUTHORS = ['Алексей', 'Мария', 'Иван', 'Ольга']


def sample_questions():
    return [
        {
            'id': number,
            'title': 'Почему не работает си',
            'text': 'gcc выдаёт ошибку bash: gcc: command not found. Что это? Стоит ли продолжить писать на Си или лучше перейти на Python?',
            'answers_count': (number * 3) % 12,
            'tags': [TAGS[number % len(TAGS)], TAGS[(number + 2) % len(TAGS)]],
            'author': AUTHORS[number % len(AUTHORS)],
            'score': 10 + number % 9,
            'created_at': '2 часа назад',
        }
        for number in range(1, 36)
    ]


def index(request):
    page = paginate(sample_questions(), request, per_page=10)
    return render(request, 'questions/index.html', {'page_obj': page, 'heading': 'Новые вопросы'})


def hot(request):
    questions = sorted(sample_questions(), key=lambda item: item['score'], reverse=True)
    page = paginate(questions, request, per_page=10)
    return render(request, 'questions/hot.html', {'page_obj': page, 'heading': 'Горячие вопросики'})


def tag(request, tag):
    questions = [item for item in sample_questions() if tag in item['tags']]
    page = paginate(questions, request, per_page=10)
    return render(request, 'questions/tag.html', {
        'page_obj': page,
        'heading': f'Вопросы по тегу: {tag}',
        'active_tag': tag,
    })


def question(request, question_id):
    questions = sample_questions()
    question_data = next((item for item in questions if item['id'] == question_id), questions[0])
    answers = [
        {'id': number, 'text': f'Вариант ответа {number}: попробуйте разбить задачу на небольшие шаги.',
         'author': AUTHORS[number % len(AUTHORS)], 'created_at': '1 час назад', 'is_correct': number == 1}
        for number in range(1, 18)
    ]
    return render(request, 'questions/question.html', {
        'question': question_data,
        'page_obj': paginate(answers, request, per_page=5),
    })


def ask(request):
    return render(request, 'questions/ask.html')
