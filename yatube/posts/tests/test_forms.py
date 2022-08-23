import shutil
import tempfile

from django.urls.base import reverse
from posts.models import User
from django.test import TestCase, Client
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group


class PostFormTests(TestCase):
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

        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.author,
            group=cls.group,
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        small_gif_second = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        cls.uploaded2 = SimpleUploadedFile(
            name='small2.gif',
            content=small_gif_second,
            content_type='image/gif'
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

    def test_create_post_create(self):
        """Создание нового поста через форму страницы post_create"""

        posts_count = Post.objects.count()

        form_data = {
            'text': 'Тестовая запись в форме нового поста',
            'group': self.group.id,
            'image': self.uploaded,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse('posts:profile', args=[self.user.username])
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                image='posts/small.gif',
            ).exists()
        )

    def test_update_post_edit(self):
        """
        При редактировании поста через форму изменяется соответствующая запись
        в базе данных.
        """

        form_data = {
            'text': 'Отредактированная запись в форме страницы post_edit',
            'group': self.group.id,
            'image': self.uploaded2,
        }

        response = self.authorized_author_client.post(
            reverse(
                'posts:post_edit',
                kwargs={
                    'username': self.author.username,
                    'post_id': self.post.id}
            ),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={
                'post_id': self.post.id}))

        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                image='posts/small2.gif',
            ).exists()
        )
