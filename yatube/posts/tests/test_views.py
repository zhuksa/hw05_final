from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post, User


class PostViewsTest(TestCase):

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

    def check_context(self, response):
        response_post = response.context.get('page_obj')[0]
        post_author = response_post.author
        post_group = response_post.group
        post_text = response_post.text
        self.assertEqual(post_author, self.author)
        self.assertEqual(post_group, self.group)
        self.assertEqual(post_text, self.post.text)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={'slug': self.group.slug}):
                        'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.post.author.username}):
                        'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}):
                        'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}):
                        'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.group, self.post.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.post.author.username})
        )
        response_post = response.context.get('page_obj')[0]
        self.assertEqual(response_post.text, self.post.text)
        self.assertEqual(response_post.author, self.post.author)
        self.assertEqual(response_post.group, self.post.group)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )

        self.assertEqual(response.context["post"].text, self.post.text)
        post_count = response.context["post"].author.posts.count()
        self.assertEqual(self.post.author.posts.count(), post_count)

    def test_create_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_show_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_edit',
                                                      kwargs={'post_id':
                                                              self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
