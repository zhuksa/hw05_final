from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name='Название группы',
        max_length=200,
        help_text='Название группы'
    )

    slug = models.SlugField('Адрес', unique=True)

    description = models.TextField(
        verbose_name='Описание группы',
        max_length=1000,
        help_text='Описание группы'
    )

    def __str__(self):
        return f'{self.title}'


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Напишите ваш пост'
    )

    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts')

    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              related_name='posts',
                              blank=True,
                              null=True)

    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments')

    text = models.TextField(verbose_name='Комментарий',
                            help_text='Комментарий')

    created = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower')

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following')

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='uniq_follow'),
        )

    def __str__(self):
        return f'{self.user}'
