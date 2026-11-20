from django.contrib import admin

from .models import Answer, AnswerLike, Question, QuestionLike, Tag


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ('author', 'text', 'is_correct')
    readonly_fields = ('author',)
    show_change_link = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'text', 'author__username')
    list_filter = ('created_at',)
    list_select_related = ('author',)
    raw_id_fields = ('author',)
    autocomplete_fields = ('tags',)
    inlines = (AnswerInline,)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'author', 'is_correct', 'created_at')
    search_fields = ('text', 'question__title', 'author__username')
    list_filter = ('is_correct', 'created_at')
    list_select_related = ('question', 'author')
    raw_id_fields = ('question', 'author')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    list_filter = (('questions', admin.EmptyFieldListFilter),)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'user')
    search_fields = ('question__title', 'user__username')
    list_filter = ('user__is_active',)
    list_select_related = ('question', 'user')
    raw_id_fields = ('question', 'user')


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'answer', 'user')
    search_fields = ('answer__text', 'user__username')
    list_filter = ('user__is_active',)
    list_select_related = ('answer', 'user')
    raw_id_fields = ('answer', 'user')
