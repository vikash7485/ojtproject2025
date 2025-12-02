import feedparser
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from datetime import datetime
from time import mktime
from news.models import News, Category

class Command(BaseCommand):
    help = 'Fetches news from RSS feeds'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting RSS fetch...")
        
        rss_feeds = [
            ('http://feeds.bbci.co.uk/news/rss.xml', 'BBC', 'World'),
            ('https://techcrunch.com/feed/', 'TechCrunch', 'Technology'),
            ('http://rss.cnn.com/rss/edition.rss', 'CNN', 'World'),
            ('https://www.theguardian.com/world/rss', 'The Guardian', 'World'),
            ('https://www.espn.com/espn/rss/news', 'ESPN', 'Sports'),
        ]

        for url, source, category_name in rss_feeds:
            self.stdout.write(f"Fetching RSS: {source}")
            feed = feedparser.parse(url)
            category, _ = Category.objects.get_or_create(name=category_name)

            for entry in feed.entries[:10]: # Limit to 10 per feed
                if News.objects.filter(link=entry.link).exists():
                    continue
                
                # Date parsing
                pub_date = None
                if hasattr(entry, 'published_parsed'):
                    try:
                        dt = datetime.fromtimestamp(mktime(entry.published_parsed))
                        pub_date = make_aware(dt)
                    except Exception:
                        pub_date = None
                
                # Image extraction (basic)
                image_url = None
                if 'media_content' in entry:
                    image_url = entry.media_content[0]['url']
                elif 'media_thumbnail' in entry:
                    image_url = entry.media_thumbnail[0]['url']
                
                News.objects.create(
                    title=entry.title[:500],
                    link=entry.link,
                    image=image_url,
                    description=entry.get('summary', '')[:500],
                    pub_date=pub_date,
                    source=source,
                    category=category,
                    guid=entry.get('id', entry.link)
                )

        self.stdout.write(self.style.SUCCESS('Successfully fetched RSS news'))
