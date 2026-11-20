from questions.shortcuts import render_with_popular_tags


def login_view(request):
    return render_with_popular_tags(request, 'core/login.html')


def signup_view(request):
    return render_with_popular_tags(request, 'core/signup.html')


def profile_view(request):
    return render_with_popular_tags(request, 'core/profile.html', show_user_profile=True)
