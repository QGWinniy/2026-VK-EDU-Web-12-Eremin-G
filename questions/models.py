from django.conf import settings
from django.db import models
from django.db.models import Count, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from django.urls import reverse


def related_count(model, field):
    counts = (
        model.objects.filter(**{field: OuterRef('pk')}).order_by()
        .values(field).annotate(total=Count('*')).values('total')
    )
    return Coalesce(Subquery(counts), Value(0))


class TagQuerySet(models.QuerySet):
    def popular(self):
        return self.annotate(question_count=Count('questions')).filter(
            question_count__gt=0,
        ).order_by('-question_count', 'name')[:7]


class Tag(models.Model):
    name = models.CharField('название', max_length=60, unique=True)
    slug = models.SlugField('адрес тега', max_length=60, unique=True)

    objects = TagQuerySet.as_manager()

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('questions:tag', args=[self.slug])


class QuestionQuerySet(models.QuerySet):
    def for_display(self):
        return self.select_related('author__profile').prefetch_related('tags').annotate(
            score=related_count(QuestionLike, 'question_id'),
            answers_count=related_count(Answer, 'question_id'),
        )

    def newest(self):
        return self.for_display().order_by('-created_at', '-pk')

    def best(self):
        return self.for_display().order_by('-score', '-created_at', '-pk')

    def by_tag(self, tag):
        return self.newest().filter(tags=tag)


class Question(models.Model):
    title = models.CharField('заголовок', max_length=150)
    text = models.TextField('текст')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='questions', verbose_name='автор',
    )
    tags = models.ManyToManyField(Tag, related_name='questions', verbose_name='теги', blank=True)
    created_at = models.DateTimeField('создан', auto_now_add=True)

    objects = QuestionQuerySet.as_manager()

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'
        indexes = [models.Index(fields=['-created_at', '-id'], name='questions_newest_idx')]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('questions:question', args=[self.pk])


class AnswerQuerySet(models.QuerySet):
    def for_question(self, question):
        return self.filter(question=question).select_related('author__profile').annotate(
            score=related_count(AnswerLike, 'answer_id'),
        ).order_by('-is_correct', 'created_at', 'pk')


class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='answers', verbose_name='вопрос',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='answers', verbose_name='автор',
    )
    text = models.TextField('текст')
    created_at = models.DateTimeField('создан', auto_now_add=True)
    is_correct = models.BooleanField('правильный ответ', default=False)

    objects = AnswerQuerySet.as_manager()

    class Meta:
        verbose_name = 'ответ'
        verbose_name_plural = 'ответы'

    def __str__(self):
        return self.text[:80]


class QuestionLike(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='likes', verbose_name='вопрос',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='question_likes', verbose_name='пользователь',
    )

    class Meta:
        verbose_name = 'лайк вопроса'
        verbose_name_plural = 'лайки вопросов'
        unique_together = [('question', 'user')]


class AnswerLike(models.Model):
    answer = models.ForeignKey(
        Answer, on_delete=models.CASCADE, related_name='likes', verbose_name='ответ',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='answer_likes', verbose_name='пользователь',
    )

    class Meta:
        verbose_name = 'лайк ответа'
        verbose_name_plural = 'лайки ответов'
        unique_together = [('answer', 'user')]
