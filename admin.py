import csv
from django.contrib import admin
from django.db.models import Count
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe

from .models import Article, Post, Tag

class TagCountFilter(admin.SimpleListFilter):
    title = 'количество тегов'
    parameter_name = 'tag_count'

    def lookups(self, request, model_admin):
        return (
            ('0', 'Без тегов'),
            ('1-3', 'От 1 до 3'),
            ('4+', '4 и больше'),
        )

    def queryset(self, request, queryset):
        queryset = queryset.annotate(tag_count=Count('tags'))

        if self.value() == '0':
            return queryset.filter(tag_count=0)
        elif self.value() == '1-3':
            return queryset.filter(tag_count__gte=1, tag_count__lte=3)
        elif self.value() == '4+':
            return queryset.filter(tag_count__gte=4)
        return queryset


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'content')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'articles_count')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _articles_count=Count('articles', distinct=True)
        )
        return queryset

    def articles_count(self, obj):
        return obj._articles_count

    articles_count.short_description = 'Количество статей'
    articles_count.admin_order_field = '_articles_count'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status_indicator', 'tags_links_display', 'created_at_formatted')
    list_filter = ['is_published', 'created_at', TagCountFilter]
    search_fields = ('title', 'content')
    actions = ['export_to_csv']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author').prefetch_related('tags')

    def status_indicator(self, obj):
        if obj.is_published:
            return mark_safe('<span style="color: #26b99a; font-weight: bold;">● Опубликовано</span>')
        return mark_safe('<span style="color: #ca4a4a; font-weight: bold;">○ Черновик</span>')

    status_indicator.short_description = 'Статус'
    status_indicator.admin_order_field = 'is_published'

    def tags_links_display(self, obj):
        tags = obj.tags.all()
        if not tags:
            return "-"

        app_label = obj._meta.app_label

        links = []
        for tag in tags:

            url = reverse(f'admin:{app_label}_tag_change', args=[tag.pk])

            links.append(f'<a href="{url}" style="text-decoration: underline; color: #447e9b;">{escape(tag.name)}</a>')

        return mark_safe(', '.join(links))

    tags_links_display.short_description = 'Теги'

    def created_at_formatted(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%d.%m.%Y %H:%M')
        return "-"

    created_at_formatted.short_description = 'Дата создания'
    created_at_formatted.admin_order_field = 'created_at'

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="articles_export.csv"'

        response.write('\ufeff'.encode('utf8'))

        writer = csv.writer(response)
        writer.writerow(['ID', 'Заголовок', 'Автор', 'Опубликовано', 'Дата создания'])

        for article in queryset:
            writer.writerow([article.id, article.title, article.author, article.is_published, article.created_at])

        return response

    export_to_csv.short_description = "Экспортировать выбранные в CSV"
