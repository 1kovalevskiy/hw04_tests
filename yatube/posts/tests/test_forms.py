from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.forms import PostForm
from posts.models import Group, Post
User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='title',
            description='description',
            slug='test-slug'
        )
        cls.user = User.objects.create_user(username='TestUser')
        Post.objects.create(
            text='text',
            author=PostFormTests.user,
            group=PostFormTests.group,
        )
        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_create_new_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Task
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый текст',
            'author': PostFormTests.user,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('index'))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с нашим слагом
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                author=PostFormTests.user,
            ).exists()
        )
