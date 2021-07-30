from django.test import TestCase
from posts.models import Group, Post
from django.contrib.auth import get_user_model

User = get_user_model()


class PostsModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(
            username='testuser',
            first_name='testuser',
            last_name='testuser',
            email='test@mail.ru'
        )

        cls.group = Group.objects.create(
            title='f'*300,
            slug='testgroup',
            description='testgroup',
        )

        cls.post = Post.objects.create(
            text='f'*300,
            author=cls.user,
            group=cls.group,
        )

    def test_str_group(self):
        group = PostsModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_str_post(self):
        post = PostsModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))
