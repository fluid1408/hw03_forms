from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="authorized")
        cls.group = Group.objects.create(
            title="Test Group",
            slug="test_slug",
            description="test description of the group",
        )
        cls.post = Post.objects.create(text="Тестовый текст поста", author=cls.user)
        cls.post = Post.objects.create(
            text="Тестовый текст поста", author=cls.user, group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def check_post_info(self, post):
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group.title, self.post.group.title)

    def test_index_page_show_correct_context(self):
        """Шаблон index.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:index"))
        self.check_post_info(response.context["page_obj"][0])
    def test_groups_page_show_correct_context(self):
        """Шаблон group_list.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug})
        )
        self.assertEqual(response.context["group"], self.group)
        self.check_post_info(response.context["page_obj"][0])

    def test_profile_page_show_correct_context(self):
        """Шаблон profile.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": self.user.username})
        )
        self.assertEqual(response.context["author"], self.user)
        self.check_post_info(response.context["page_obj"][0])


    def test_detail_page_show_correct_context(self):
        """Шаблон post_detail.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )
        post_text_0 = {
            response.context["post"].text: "Тестовый пост",
            response.context["post"].group: self.group,
            response.context["post"].author: self.user.username,
        }
        for value, expected in post_text_0.items():
            self.assertEqual(post_text_0[value], expected)
            self.check_post_info(response.context["post"])

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)
    