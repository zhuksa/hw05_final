from django.test import Client, TestCase
from http import HTTPStatus

from ..models import Group, Post, User


class TaskURLTestsPost(TestCase):
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

    def test_authorized_pages(self):
        """Тестируем доступность страниц авторизованными пользователями и
        доступность страниц автором."""
        post = TaskURLTestsPost.post
        urls = {
            '/create/': HTTPStatus.OK,
            f'/posts/{post.id}/edit/': HTTPStatus.OK,
        }
        for field, expected_value in urls.items():
            with self.subTest(field=field):
                response = self.authorized_client.get(field)
                self.assertEqual(response.status_code, expected_value)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/profile.html': '/profile/author/',
            'posts/post_detail.html': f'/posts/{self.post.id}/',
            'posts/create_post.html': f'/posts/{self.post.id}/edit/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_author_templates(self):
        """Тестируем шаблоны страниц авторизованного пользователя и автора."""
        post = TaskURLTestsPost.post
        url_templates = {
            '/create/': 'posts/create_post.html',
            f'/posts/{post.id}/edit/': 'posts/create_post.html',
        }
        for url, expected_template in url_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, expected_template)

    def test_guest_pages(self):
        """Тестируем доступность страниц неавторизованными пользователями."""
        post = TaskURLTestsPost.post
        urls = {
            '/': HTTPStatus.OK,
            '/profile/author/': HTTPStatus.OK,
            f'/posts/{post.id}/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for field, expected_value in urls.items():
            with self.subTest(field=field):
                response = self.guest_client.get(field)
                self.assertEqual(response.status_code, expected_value)
