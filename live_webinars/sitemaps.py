from django.contrib.sitemaps import Sitemap
from live_webinars.models import LiveWebinar

class WebinarSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return LiveWebinar.objects.exclude(is_test=True)

    def lastmod(self, obj):
        return obj.created_at