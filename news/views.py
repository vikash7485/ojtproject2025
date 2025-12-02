from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from .models import News, Category, SavedArticle

from django.db.models import Q

import requests
from django.conf import settings
from django.utils.dateparse import parse_datetime

def home(request):
    category_id = request.GET.get('category')
    search_query = request.GET.get('q')
    
    # Default: Show local DB news (RSS)
    news_list = News.objects.all()
    
    if category_id:
        news_list = news_list.filter(category_id=category_id)
    
    # Global Search: Call NewsAPI Everything
    if search_query:
        api_key = settings.NEWSAPI_KEY
        # Only call API if key is configured
        if api_key:
            url = f'https://newsapi.org/v2/everything?q={search_query}&apiKey={api_key}&language=en&sortBy=publishedAt'
            
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for article in data.get('articles', []):
                        # Skip if URL is missing
                        if not article.get('url'):
                            continue
                        
                        # Deduplicate & Save
                        if not News.objects.filter(link=article['url']).exists():
                            # Determine category (optional, or just leave null)
                            category = None 
                            
                            pub_date = parse_datetime(article['publishedAt']) if article.get('publishedAt') else None
                            
                            News.objects.create(
                                title=article.get('title') or 'No Title',
                                link=article['url'],
                                image=article.get('urlToImage') or '',
                                description=article.get('description') or '',
                                content=article.get('content') or '',
                                author=article.get('author') or '',
                                pub_date=pub_date,
                                source=article.get('source', {}).get('name', 'Unknown'),
                                category=category
                            )
                    
                    # Filter DB again to include newly fetched articles
                    news_list = News.objects.filter(
                        Q(title__icontains=search_query) | 
                        Q(description__icontains=search_query)
                    )
                elif response.status_code == 426:
                    messages.warning(request, 'NewsAPI rate limit reached. Showing cached results.')
                    news_list = news_list.filter(
                        Q(title__icontains=search_query) | 
                        Q(description__icontains=search_query)
                    )
            except requests.exceptions.Timeout:
                messages.warning(request, 'API request timed out. Showing cached results.')
                news_list = news_list.filter(
                    Q(title__icontains=search_query) | 
                    Q(description__icontains=search_query)
                )
            except Exception as e:
                print(f"Error fetching from API: {e}")
                messages.warning(request, 'Unable to fetch latest news. Showing cached results.')
                # Fallback to local search if API fails
                news_list = news_list.filter(
                    Q(title__icontains=search_query) | 
                    Q(description__icontains=search_query)
                )
        else:
            # No API key configured, search local DB only
            messages.info(request, 'Searching local news database.')
            news_list = news_list.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query)
            )

    paginator = Paginator(news_list, 20) # 20 articles per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    # Check which articles are saved by the user
    saved_news_ids = []
    if request.user.is_authenticated:
        saved_news_ids = SavedArticle.objects.filter(user=request.user).values_list('news_id', flat=True)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'saved_news_ids': saved_news_ids,
        'selected_category': int(category_id) if category_id else None
    }
    return render(request, 'news/home.html', context)

@login_required
def saved_articles(request):
    saved_list = SavedArticle.objects.filter(user=request.user).select_related('news').order_by('-saved_date')
    
    paginator = Paginator(saved_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'news/saved.html', {'page_obj': page_obj})

@login_required
def toggle_save(request, news_id):
    news = get_object_or_404(News, id=news_id)
    saved_article, created = SavedArticle.objects.get_or_create(user=request.user, news=news)
    
    if not created:
        # If already exists, delete it (toggle off)
        saved_article.delete()
        messages.success(request, 'Article removed from saved list.')
    else:
        messages.success(request, 'Article saved.')
    
    # Redirect back to where the user came from
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
