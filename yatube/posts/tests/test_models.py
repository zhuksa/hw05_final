from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Post, Group


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='ivan')

        cls.group = Group.objects.create(
            title='Название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )

        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.author,
            group=cls.group,
        )

    def test_post_verbose_name(self):
        """verbose_name в модели Post совпадает"""

        post = PostModelTest.post
        verbose_fields = {
            'text': 'Текст',
        }

        for value, expected in verbose_fields.items():
            self.assertEqual(
                post._meta.get_field(value).verbose_name,
                expected)

    def test_help_text_is_text_field(self):
        """help_text в модели Post совпадает"""

        post = PostModelTest.post
        help_text_fields = {
            'text': 'Напишите ваш пост',
        }

        for value, expected in help_text_fields.items():
            self.assertEqual(
                post._meta.get_field(value).help_text,
                expected)

    def test_post_is_text_fild(self):
        """В поле __str__  объекта post записано значение поля post.text."""

        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='ivan')

        cls.group = Group.objects.create(
            title='Название группы',
            description='Тестовое описание группы',
        )

        cls.post = Post.objects.create(
            text='Текст',
            author=cls.author,
            group=cls.group,
        )

    def test_group_verbose_name(self):
        """verbose_name в модели Group совпадает"""

        group = GroupModelTest.group
        verbose_fields = {
            'title': 'Название группы',
            'description': 'Описание группы',
        }

        for value, expected in verbose_fields.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name,
                    expected)

    def test_help_text_name(self):
        """help_text в модели Group совпадает"""
        group = GroupModelTest.group
        help_text_fields = {
            'title': 'Название группы',
            'description': 'Описание группы',
        }
        for value, expected in help_text_fields.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text,
                    expected)

    def test_group_name_is_title_fild(self):
        """В поле __str__  объекта group записано значение поля group.title."""

        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
