from captcha.fields import CaptchaField
from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    captcha = CaptchaField()

    class Meta:
        model = Comment
        fields = ['name', 'email', 'subject', 'content', 'post', 'captcha']
        readonly_fields = ('published_date',)

        widgets = {
            'post': forms.HiddenInput()
        }
