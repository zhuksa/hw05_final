from django.forms import ModelForm, Textarea

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        help_texts = {
            'text': 'Hапишите свой пост здесь',
            'group': 'Выберите сообщество',
            'image': 'Вставьте картинку',
        }

        labels = {
            'text': 'Текст',
            'group': 'Сообщество',
            'image': 'Картинка',
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        help_texts = {'text': 'Hапишите комментарий'}
        labels = {'text': 'Комментарий'}
        widgets = {'text': Textarea(attrs={'class': 'form-control'})}
