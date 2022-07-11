from django.test import Client, TestCase
from ..models import Group, Post, User


class PostViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='author
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
