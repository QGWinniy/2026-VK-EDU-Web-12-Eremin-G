from uuid import uuid4

from django import forms
from django.db import transaction
from django.db.models import Sum
from django.utils.text import slugify

from .models import Answer, Question, Tag


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(label='Теги', help_text='Перечислите теги через запятую.')

    class Meta:
        model = Question
        fields = ('title', 'text')

    def clean_tags(self):
        names = dict.fromkeys(name.strip() for name in self.cleaned_data['tags'].split(','))
        names.pop('', None)
        if not names:
            raise forms.ValidationError('Укажите хотя бы один тег.')
        if any(len(name) > 60 for name in names):
            raise forms.ValidationError('Название тега не должно превышать 60 символов.')
        return names

    @transaction.atomic
    def save(self, *, author):
        self.instance.author = author
        question = super().save()
        tags = []
        for name in self.cleaned_data['tags']:
            slug = slugify(name)[:27] or 'tag'
            tag, _ = Tag.objects.get_or_create(
                name=name, defaults={'slug': f'{slug}-{uuid4().hex}'},
            )
            tags.append(tag)
        question.tags.set(tags)
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text',)
        labels = {'text': 'Текст ответа'}
        widgets = {'text': forms.Textarea(attrs={'rows': 4})}

    def save(self, *, author, question):
        self.instance.author = author
        self.instance.question = question
        return super().save()


class VoteForm(forms.Form):
    value = forms.TypedChoiceField(choices=[('1', 'Лайк'), ('-1', 'Дизлайк')], coerce=int)

    def __init__(self, data, *, user, model):
        super().__init__(data)
        self.user = user
        self.fields['id'] = forms.ModelChoiceField(queryset=model.objects.select_for_update())

    def clean(self):
        data = super().clean()
        if 'id' in data and 'value' in data:
            self.votes = data['id'].likes
            self.vote = self.votes.filter(user=self.user).first()
            if self.vote and self.vote.value == data['value']:
                raise forms.ValidationError('Вы уже поставили эту оценку.', code='duplicate')
        return data

    def save(self):
        value = self.cleaned_data['value']
        if self.vote is None:
            self.votes.create(user=self.user, value=value)
        else:
            self.vote.value = value
            self.vote.save(update_fields=['value'])
        score = self.votes.aggregate(score=Sum('value', default=0))['score']
        return {'score': score, 'value': value}


class CorrectAnswerForm(forms.Form):
    question_id = forms.ModelChoiceField(queryset=Question.objects.select_for_update())
    answer_id = forms.ModelChoiceField(queryset=Answer.objects.all())

    def __init__(self, data, *, user):
        super().__init__(data)
        self.user = user

    def clean(self):
        data = super().clean()
        if 'question_id' in data and 'answer_id' in data:
            question, answer = data['question_id'], data['answer_id']
            if question.author_id != self.user.pk:
                raise forms.ValidationError('Только автор вопроса может выбрать ответ.', code='forbidden')
            if answer.question_id != question.pk:
                raise forms.ValidationError('Ответ относится к другому вопросу.')
            if answer.is_correct:
                raise forms.ValidationError('Этот ответ уже отмечен.', code='duplicate')
        return data

    def save(self):
        question, answer = self.cleaned_data['question_id'], self.cleaned_data['answer_id']
        question.answers.filter(is_correct=True).update(is_correct=False)
        answer.is_correct = True
        answer.save(update_fields=['is_correct'])
        return {'answer_id': answer.pk}
