from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Post, Group


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='avtor')
        cls.user = User.objects.create_user(username='client')

        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.author,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(self.author)

    def test_url_exists_at_desired_location(self):
        """Страница доступна любому пользователю."""

        url_address_names = (
            '/',
            f'/group/{self.group.slug}/',
            f'/{self.author.username}/',
            f'/{self.author.username}/{self.post.id}/',
        )

        for address in url_address_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_url_names = {
            'posts/index.html': '/',
            'posts/group.html': f'/group/{self.group.slug}/',
            'posts/new_post.html': '/new/',
            'posts/profile.html': f'/{self.author.username}/',
            'posts/post.html': f'/{self.author.username}/{self.post.id}/',
        }

        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_new_exists_at_desired_location_authorized(self):
        """Страница доступна авторизованному пользователю."""

        response = self.authorized_author_client.get('/new/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exist_at_desired_location_authorized(self):
        """Страница доступна авторизованному пользователю."""

        url_address_names = (
            f'/{self.author.username}/follow/',
            f'/{self.author.username}/unfollow/',
        )

        for address in url_address_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_new_post_redirect_anonymous_on_admin_login(self):
        """Страница 'new_post' перенаправит анонимного
        пользователя на страницу логина."""

        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/new/')

    def test_post_edit_uses_correct_template(self):
        """post_edit использует соответствующий шаблон."""

        response = self.authorized_author_client.get(
            f'/{self.author.username}/{self.post.id}/edit/')
        self.assertTemplateUsed(response, 'posts/new_post.html')

    def test_post_edit_exists_for_author(self):
        """Страница 'post_edit' доступна автору поста."""

        response = self.authorized_author_client.get(
            f'/{self.author.username}/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_redirect_anonymous_on_admin_login(self):
        """Страница 'post_edit' перенаправит анонимного
        пользователя на страницу логина."""

        response = self.guest_client.get(
            f'/{self.author.username}/{self.post.id}/edit/')

        self.assertRedirects(
            response, ('/auth/login/?next=/'
                       f'{self.author.username}/{self.post.id}/edit/')
        )

    def test_post_edit_redirect_auth_on_post_view(self):
        """Страница 'post_edit' перенаправит авторизованного не автора
        на страницу поста."""

        response = self.authorized_client.get(
            f'/{self.author.username}/{self.post.id}/edit/', follow=True)
        self.assertRedirects(
            response, f'/{self.author.username}/{self.post.id}/')
