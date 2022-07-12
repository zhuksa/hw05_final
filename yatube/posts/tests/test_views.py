import shutil
import tempfile

from django.contrib.auth import get_user_model
from django import forms
from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group


User = get_user_model()


class PostPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='ivan')
        cls.user = User.objects.create_user(username='oleg')

        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )

        cls.group_2 = Group.objects.create(
            title='Тестовый заголовок группы 2',
            slug='test_slug_2',
            description='Тестовое описание группы 2',
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.author,
            group=cls.group,
            image=uploaded,
        )

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(self.author)

    def test_pages_use_accessible_by_name(self):
        """URL доступен."""

        url_address_names = {
            reverse('posts:index'),
            reverse('posts:new_post')
        }

        for address in url_address_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_use_correct_template(self):
        """Page использует соответствующий шаблон."""

        templates_page_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/new_post.html': reverse('posts:new_post'),
        }

        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_uses_correct_context(self):
        """Index использует соответствующий контекст."""

        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'].object_list[0]
        post_text_0 = first_object.text

        self.assertEqual(
            post_text_0,
            'Тестовая запись в форме нового поста',
            'Неверный текст поста на главной странице'
        )

    def test_new_post_uses_correct_context(self):
        """New_post использует соответствующий контекст."""

        response = self.authorized_client.get(reverse('posts:new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_uses_correct_context(self):
        """Profile использует соответствующий контекст."""

        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.author.username})
        )

        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_pic_0 = first_object.image

        self.assertEqual(
            post_text_0,
            'Тестовый текст поста',
            'Неверный текст поста на странице профиля'
        )
        self.assertEqual(
            post_author_0,
            f'{self.author.username}',
            'Неверный автор поста на странице профиля'
        )
        self.assertEqual(
            post_pic_0,
            f'{self.post.image}',
            'Неверный текст поста на главной странице'
        )

    def test_post_view_uses_correct_context(self):
        """Post_view использует соответствующий контекст."""

        response = self.guest_client.get(reverse(
            'posts:post',
            kwargs={'username': self.author.username, 'post_id': self.post.id})
        )

        self.assertEqual(response.context['post_view'].text,
                         self.post.text,
                         'Неверный текст поста на странице поста')

        self.assertEqual(response.context['post_view'].author.username,
                         self.author.username,
                         'Неверный автор поста на странице поста')
        self.assertEqual(response.context['post_view'].image,
                         self.post.image,
                         'Неверная картинка на странице поста')

    def test_post_edit_uses_correct_context(self):
        """Post_edit использует соответствующий контекст."""

        response = self.authorized_author_client.get(reverse(
            'posts:post_edit',
            kwargs={
                'username': self.author.username,
                'post_id': self.post.id}),
        )

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_page_not_found(self):
        """ Доступ к несуществующей странице. """
        response = self.guest_client.get('misc/404.html')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_add_follow(self):
        """ подписка: обращаешься к follow_index, через context['page'].object_list[0]
        находишь количество подписок, и сравниваешь их с 0, т.е проверяешь,
        что еще не подписалась ни на кого, затем подписываешься
        self.follower_client.get(reverse('profile_follow',
        kwargs{'username': self.post.author})) и проверяешь,
        что подписалась, сравнение уже будет с 1"""

        # проверяем, что follower_client еще не подписан на автора поста
        response_1 = self.authorized_client.get(reverse('posts:follow_index'))
        page_object_1 = response_1.context['page_obj'].object_list
        self.assertEqual((len(page_object_1)), 0)

        # подписываемся на автора поста
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.post.author})
        )
        # проверяем, что follower_client подписался
        response_2 = self.authorized_client.get(reverse('posts:follow_index'))
        page_object_2 = response_2.context['page_obj'].object_list
        self.assertEqual((len(page_object_2)), 1)

    def test_unfollow(self):
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.post.author})
        )

        response_1 = self.authorized_client.get(reverse('posts:follow_index'))
        page_object_1 = response_1.context['page_obj'].object_list

        self.assertEqual((len(page_object_1)), 1)

        self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.post.author})
        )

        response_2 = self.authorized_client.get(reverse('posts:follow_index'))
        page_object_2 = response_2.context['page_obj'].object_list
        self.assertEqual((len(page_object_2)), 0)


class PaginatorPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create(
            first_name='Иван',
            last_name='Иванов',
            username='Ivan',
            email='ivan@ivan.ru',
        )

        for i in range(1, 13):
            cls.post = Post.objects.create(
                text='Тестовый текст поста {i}',
                author=user,
            )

    def test_first_page_contains_ten_posts(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 2)

    def test_second_page_contains_two_posts(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 2)
