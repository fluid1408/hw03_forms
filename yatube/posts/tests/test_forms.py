import shutil
import tempfile

from django.contrib.auth import get_user_model
from ..models import Post, Group
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

User = get_user_model()

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание группы",
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами 
        # для управления файлами и директориями: 
        # создание, удаление, копирование, перемещение, изменение папок и файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()  
        # Для тестирования загрузки изображений 
        # берём байт-последовательность картинки, 
        # состоящей из двух пикселей: белого и чёрного
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post = Post.objects.first()
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:profile', kwargs = {"username": self.user.username}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count+1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(post.author, self.user)

    def test_edit_post(self):
        self.post = Post.objects.create(text = 'Тестовый текст', group = self.group, author = self.user)
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'pk':self.post.pk}), data = form_data, follow=True)
        self.post.refresh_from_db()
        self.assertRedirects(response, reverse('posts:post_detail', kwargs = {"post_id": self.post.id}))
        self.assertEqual(self.post.text, form_data["text"])
        self.assertEqual(self.post.group.pk, form_data["group"])
        self.assertEqual(self.post.author, self.post.author)