from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import transaction

from .models import Profile


class SignupForm(UserCreationForm):
    email = forms.EmailField(label='Электронная почта')
    first_name = forms.CharField(label='Имя', max_length=150)

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email', 'first_name')

    @transaction.atomic
    def save(self):
        user = super().save()
        Profile.objects.create(user=user)
        return user


class ProfileForm(forms.ModelForm):
    email = forms.EmailField(label='Электронная почта')
    nick = forms.CharField(label='Ник', max_length=150)
    avatar = forms.ImageField(
        label='Аватар', required=False,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp'])],
        help_text='JPG, PNG, GIF или WebP, до 5 МБ.',
    )

    class Meta:
        model = Profile
        fields = ('email', 'nick', 'avatar')

    def __init__(self, *args, user, **kwargs):
        self.user = user
        profile = getattr(user, 'profile', None) or Profile(user_id=user.pk)
        super().__init__(
            *args, instance=profile,
            initial={'email': user.email, 'nick': user.first_name or user.username},
            **kwargs,
        )

    def clean_avatar(self):
        avatar = self.cleaned_data['avatar']
        if 'avatar' in self.files and avatar.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Размер аватара не должен превышать 5 МБ.')
        return avatar

    @transaction.atomic
    def save(self):
        self.user.email = self.cleaned_data['email']
        self.user.first_name = self.cleaned_data['nick']
        self.user.save(update_fields=['email', 'first_name'])
        defaults = {}
        if 'avatar' in self.changed_data:
            defaults['avatar'] = self.cleaned_data['avatar'] or ''
        profile, _ = Profile.objects.update_or_create(user=self.user, defaults=defaults)
        return profile
