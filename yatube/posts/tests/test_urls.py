from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Post, Group
from http import HTTPStatus

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="authorized")
        cls.user_not = User.objects.create_user(username="not_authorized")
        cls.group = Group.objects.create(
            title="Test Group",
            slug="test-slug",
            description="test description of the group",
        )
        cls.post = Post.objects.create(text="test post", author=cls.user)

    def setUp(self):
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user_not)
        self.author = Client()
        self.author.force_login(self.user)


    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            "/": "posts/index.html",
            f"/group/{self.group.slug}/": "posts/group_list.html",
            f"/profile/{self.user}/": "posts/profile.html",
            f"/posts/{self.post.id}/": "posts/post_detail.html",
            f"/posts/{self.post.pk}/edit/": "posts/create_post.html",
            "/create/": "posts/create_post.html",
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.author.get(address)
                self.assertTemplateUsed(response, template)
    
    def test_404(self):
        """Проверяем возвращает ли сервер код 404, если страница не найдена"""
        response = self.client.get("/404/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


    def test_URLs_users_acces_guest(self):
        page_list = {
        '/': HTTPStatus.OK,
        '/create/': HTTPStatus.FOUND,
        f'/posts/{self.post.pk}/': HTTPStatus.FOUND,
        f'/posts/{self.post.id}/': HTTPStatus.OK,
        f'/profile/{self.user}/': HTTPStatus.OK,
        f'/group/{self.group.slug}/': HTTPStatus.OK,
        }
        for address, code_status in page_list.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, code_status)