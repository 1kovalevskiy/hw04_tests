from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from time import sleep

from posts.models import Group, Post

User = get_user_model()


class PostPageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group1 = Group.objects.create(
            title='title',
            description='description',
            slug='test-group1'
        )
        cls.group2 = Group.objects.create(
            title='title2',
            description='description2',
            slug='test-group2'
        )
        cls.group3 = Group.objects.create(
            title='title3',
            description='description3',
            slug='test-group3'
        )
        cls.user = User.objects.create_user(username='TestUser')
        # Не уверен, что через bulk_create у них будет разная дата создания
        for i in range(13):
            Post.objects.create(
                text=f'text{i}',
                author=PostPageTests.user,
                group=PostPageTests.group1,
            )
            # пришлось ввести задержку, чтобы посты создавались в разное время
            # а то последним иногда был и 11, и 10 пост, вместо 12!
            sleep(0.005)
        cls.templates_page_names = {
            'posts/index.html': reverse('index'),
            'posts/new_post.html': reverse('new_post'),
            'posts/group.html': reverse('group_posts',
                                        args=[PostPageTests.group1.slug]),
        }
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        cls.page_with_post_list = [
            reverse('index'),
            reverse('group_posts', args=[PostPageTests.group1.slug]),
            reverse('profile', args=[PostPageTests.user.username]),
        ]

    def setUp(self):
        # Создаём неавторизованный клиент
        self.guest_client = Client()
        # Создаём авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPageTests.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in (
            PostPageTests.templates_page_names.items()
        ):
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_first_page_contains_ten_records(self):
        """Пагинатор передал 10 постов на первую страницу и 3 на вторую"""
        for url in PostPageTests.page_with_post_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(len(response.context['page']), 10)
                response2 = self.guest_client.get(url + '?page=2')
                self.assertEqual(len(response2.context['page']), 3)

    def test_page_with_list_show_correct_context(self):
        """
        Шаблоны страниц со списками постов сформированы\
        с правильным контекстом.
        """
        for url in PostPageTests.page_with_post_list:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                # Взяли первый элемент из списка и проверили, что его
                # содержание совпадает с ожидаемым
                first_object = response.context['page'][0]
                task_text_0 = first_object.text
                task_author_0 = first_object.author
                task_group_0 = first_object.group
                self.assertEqual(task_text_0, 'text12')
                self.assertEqual(task_author_0, PostPageTests.user)
                self.assertEqual(task_group_0, PostPageTests.group1)

    def test_page_with_form_show_correct_context(self):
        """Шаблоны с формами сформированы с правильным контекстом."""
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        page_with_form = ['/new/', '/TestUser/12/edit/']
        for url in page_with_form:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                for value, expected in PostPageTests.form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context['form'].fields[value]
                        self.assertIsInstance(form_field, expected)

    def test_page_with_post_show_correct_context(self):
        """
        Шаблон поста сформированы с правильным контекстом.
        """
        pk = Post.objects.filter(text='text11').get().pk
        response = self.authorized_client.get(f'/TestUser/{pk}/')
        # Взяли первый элемент из списка и проверили, что его
        # содержание совпадает с ожидаемым
        post = response.context['post']
        task_text_0 = post.text
        task_author_0 = post.author
        task_group_0 = post.group
        self.assertEqual(task_text_0, 'text11')
        self.assertEqual(task_author_0, PostPageTests.user)
        self.assertEqual(task_group_0, PostPageTests.group1)

    def test_create_new_post_and_show_in_group1(self):
        """Запись создалась и отображается в группе 1"""
        Post.objects.create(
            text='new-post',
            author=PostPageTests.user,
            group=PostPageTests.group1,
        )
        for url in PostPageTests.page_with_post_list:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                post = response.context['page'][0]
                self.assertEqual(post.text, 'new-post')

    def test_group2_is_empty(self):
        """Запись не отображается в группе 2"""
        self.group4 = Group.objects.create(
            title='title4',
            description='description4',
            slug='test-group4'
        )
        Post.objects.create(
            text='new-post',
            author=PostPageTests.user,
            group=PostPageTests.group1,
        )
        response = self.authorized_client.get(
            reverse('group_posts', args=[self.group4.slug]))
        objects = response.context['page']
        # Не получается с count
        self.assertEqual(len(objects), 0)
