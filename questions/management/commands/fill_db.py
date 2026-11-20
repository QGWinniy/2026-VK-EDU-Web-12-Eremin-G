from random import Random
from time import monotonic
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from faker import Faker

from core.models import Profile
from questions.models import Answer, AnswerLike, Question, QuestionLike, Tag


BATCH_SIZE = 5000
QUESTION_BATCH_SIZE = 500
QUESTIONS_PER_USER = 10
ANSWERS_PER_QUESTION = 10
LIKES_PER_QUESTION_WITH_ANSWERS = 20


def batches(items, size):
    for start in range(0, len(items), size):
        yield items[start:start + size]


def question_like_count(question_id, user_count):
    return 1 + question_id % min(10, user_count)


class Command(BaseCommand):
    help = 'Добавляет тестовые данные. Для выполнения всех порогов ДЗ укажите ratio=10001.'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def handle(self, *args, **options):
        ratio = options['ratio']
        if ratio < 2:
            raise CommandError('ratio должен быть не меньше 2 для создания уникальных лайков.')

        started_at = monotonic()
        fake = Faker('ru_RU')
        random = Random()
        user_model = get_user_model()
        namespace = uuid4().hex[:16]
        self.log(f'Начинаю наполнение. Идентификатор запуска: {namespace}.')
        users = self.insert(
            'пользователи', user_model, range(ratio), BATCH_SIZE,
            lambda batch: [
                user_model(
                    username=f'seed_{namespace}_{number}', first_name=fake.first_name(),
                    last_name=fake.last_name(), password=make_password(None),
                )
                for number in batch
            ], collect_ids=True,
        )
        self.insert('профили', Profile, users, BATCH_SIZE, lambda batch: [
            Profile(user_id=user_id) for user_id in batch
        ])
        tags = self.insert('теги', Tag, range(1, ratio + 1), BATCH_SIZE, lambda batch: [
            Tag(
                name=f'{fake.word().capitalize()[:20]} {number} ({namespace})',
                slug=f'tema-{namespace}-{number}',
            )
            for number in batch
        ], collect_ids=True)
        questions = self.insert(
            'вопросы', Question, range(ratio * QUESTIONS_PER_USER), QUESTION_BATCH_SIZE,
            lambda batch: [
                Question(title=fake.sentence()[:150], text=fake.paragraph(), author_id=random.choice(users))
                for _ in batch
            ], collect_ids=True,
        )
        through = Question.tags.through
        self.insert('связи вопросов с тегами', through, questions, QUESTION_BATCH_SIZE, lambda batch: [
            through(question_id=question_id, tag_id=tag_id)
            for question_id in batch
            for tag_id in random.sample(tags, min(3, len(tags)))
        ])
        answers = self.insert('ответы', Answer, questions, QUESTION_BATCH_SIZE, lambda batch: [
            Answer(
                question_id=question_id, author_id=random.choice(users),
                text=fake.paragraph(), is_correct=index == 0,
            )
            for question_id in batch
            for index in range(ANSWERS_PER_QUESTION)
        ], collect_ids=True)
        self.insert('лайки вопросов', QuestionLike, questions, QUESTION_BATCH_SIZE, lambda batch: [
            QuestionLike(question_id=question_id, user_id=user_id)
            for question_id in batch
            for user_id in random.sample(users, question_like_count(question_id, len(users)))
        ])
        self.insert(
            'лайки ответов', AnswerLike, range(len(questions)), QUESTION_BATCH_SIZE,
            lambda batch: self.answer_likes(batch, questions, answers, users, random),
        )
        self.log(self.style.SUCCESS(f'Наполнение завершено за {monotonic() - started_at:.0f} с.'))

    def log(self, message):
        self.stdout.write(message)
        self.stdout.flush()

    def insert(self, label, model, items, batch_size, build_rows, *, collect_ids=False):
        self.log(f'Этап «{label}» начат.')
        ids = []
        processed = 0
        inserted = 0
        with transaction.atomic():
            for batch in batches(items, batch_size):
                rows = model.objects.bulk_create(build_rows(batch), batch_size=BATCH_SIZE)
                if collect_ids:
                    ids.extend(row.pk for row in rows)
                inserted += len(rows)
                processed += len(batch)
                self.log(
                    f'{label.capitalize()}: подготовлено {inserted} записей, '
                    f'прогресс этапа {processed / len(items):.1%}.'
                )
            self.log(f'Фиксирую этап «{label}» в PostgreSQL…')
        self.log(f'Этап «{label}» завершён. В базе добавлено {inserted} записей.')
        return ids

    def answer_likes(self, batch, questions, answers, users, random):
        likes = []
        for question_index in batch:
            question_id = questions[question_index]
            count = LIKES_PER_QUESTION_WITH_ANSWERS - question_like_count(question_id, len(users))
            first_answer = question_index * ANSWERS_PER_QUESTION
            for index, answer_id in enumerate(answers[first_answer:first_answer + ANSWERS_PER_QUESTION]):
                vote_count = 1 + (index < count - ANSWERS_PER_QUESTION)
                likes.extend(
                    AnswerLike(answer_id=answer_id, user_id=user_id)
                    for user_id in random.sample(users, vote_count)
                )
        return likes
