from django.shortcuts import render

from .models import Tag


def render_with_popular_tags(request, template, **context):
    return render(request, template, {
        **context,
        'show_popular_tags': True,
        'popular_tags': Tag.objects.popular(),
    })
