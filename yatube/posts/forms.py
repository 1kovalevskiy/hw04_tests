from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["text", "group"]
        help_texts = {
            "text": "Здесь должен быть текст поста",
            "group": "А здесь можно выбрать группу для опубликования"
        }
        labels = {
            "text": "Текст поста",
            "group": "Группа"
        }
