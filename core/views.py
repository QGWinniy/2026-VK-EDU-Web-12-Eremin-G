from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect

from questions.models import Tag
from questions.shortcuts import render_with_popular_tags

from .forms import ProfileForm, SignupForm


class Login(LoginView):
    template_name = 'core/login.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            show_popular_tags=True, popular_tags=Tag.objects.popular(), **kwargs,
        )


class Logout(LogoutView):
    next_page = 'questions:index'


def signup_view(request):
    form = SignupForm(request.POST if request.method == 'POST' else None)
    if form.is_valid():
        form.save()
        return redirect('questions:index')
    return render_with_popular_tags(request, 'core/signup.html', form=form)


@login_required
def profile_view(request):
    form = ProfileForm(
        request.POST if request.method == 'POST' else None,
        request.FILES if request.method == 'POST' else None,
        user=request.user,
    )
    if form.is_valid():
        form.save()
        return redirect('core:profile')
    return render_with_popular_tags(request, 'core/profile.html', form=form)
