from django.test import Client, TestCase
from django.urls import reverse
from django.shortcuts import get_object_or_404

from ..models import Group, Post, User


class PostEditFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post"""
        form_data = {
            'text': self.post.text,
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user})
        )

    def test_edit_post(self):
        """Валидная форма редактирует существующую базу"""
        post = Post.objects.create(
            author=self.user,
            group=self.group,
            text='Текстовый пост'
        )
        form_data = {
            'text': 'Измененный текстовый текст текстового поста',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(post.id,)),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs={'post_id': post.id}))

        post_number = get_object_or_404(Post, id=post.id)
        self.assertEqual(post_number.text,
                         'Измененный текстовый текст текстового поста')
