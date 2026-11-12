from django.shortcuts import render
from .models import Article

def post_list(request):
    articles = Article.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'blog/list.html', {'articles': articles})


