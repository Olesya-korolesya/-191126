from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    image = models.ImageField(upload_to='posts/', blank=True, null=True, verbose_name="Изображение")

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Слаг")

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles', verbose_name="Автор")
    content = models.TextField(verbose_name="Содержание")
    is_published = models.BooleanField(default=False, verbose_name="Опубликовано")
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True, verbose_name="Теги")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    image = models.ImageField(
        upload_to='articles/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Изображение')

    def __str__(self):
        return self.title