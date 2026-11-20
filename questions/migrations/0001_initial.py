from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, unique=True, verbose_name='название')),
                ('slug', models.SlugField(max_length=60, unique=True, verbose_name='адрес тега')),
            ],
            options={'verbose_name': 'тег', 'verbose_name_plural': 'теги', 'ordering': ('name',)},
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150, verbose_name='заголовок')),
                ('text', models.TextField(verbose_name='текст')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='создан')),
                ('author', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, related_name='questions',
                    to=settings.AUTH_USER_MODEL, verbose_name='автор',
                )),
                ('tags', models.ManyToManyField(
                    blank=True, related_name='questions', to='questions.tag', verbose_name='теги',
                )),
            ],
            options={
                'verbose_name': 'вопрос',
                'verbose_name_plural': 'вопросы',
                'indexes': [models.Index(fields=['-created_at', '-id'], name='questions_newest_idx')],
            },
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='текст')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='создан')),
                ('is_correct', models.BooleanField(default=False, verbose_name='правильный ответ')),
                ('author', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, related_name='answers',
                    to=settings.AUTH_USER_MODEL, verbose_name='автор',
                )),
                ('question', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, related_name='answers',
                    to='questions.question', verbose_name='вопрос',
                )),
            ],
            options={'verbose_name': 'ответ', 'verbose_name_plural': 'ответы'},
        ),
        migrations.CreateModel(
            name='QuestionLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, related_name='likes',
                    to='questions.question', verbose_name='вопрос',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, related_name='question_likes',
                    to=settings.AUTH_USER_MODEL, verbose_name='пользователь',
                )),
            ],
            options={
                'verbose_name': 'лайк вопроса',
                'verbose_name_plural': 'лайки вопросов',
                'unique_together': {('question', 'user')},
            },
        ),
        migrations.CreateModel(
            name='AnswerLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, related_name='likes',
                    to='questions.answer', verbose_name='ответ',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, related_name='answer_likes',
                    to=settings.AUTH_USER_MODEL, verbose_name='пользователь',
                )),
            ],
            options={
                'verbose_name': 'лайк ответа',
                'verbose_name_plural': 'лайки ответов',
                'unique_together': {('answer', 'user')},
            },
        ),
    ]
