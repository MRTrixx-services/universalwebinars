from django.urls import path
from .views import home,about_view,contact_view,privacy,refund,terms,shipping,watch_demo,search_webinars,newsletter_subscribe,dismiss_promo

app_name = "home"

urlpatterns = [
    path("", home, name="home"),
    path("about/", about_view, name="about"),
    path("contact/", contact_view, name="contact"),
    path("privacy-policy/", privacy, name="privacy"),
    path("refund-policy/", refund, name="refund"),
    path("terms/", terms, name="terms"),
    path("shipping-return/", shipping, name="shipping"),
    path("watch-demo/", watch_demo, name="watch_demo"),
    path("search/", search_webinars, name="search"),
    path("newsletter/subscribe/", newsletter_subscribe, name="newsletter_subscribe"),
    path("promo/dismiss/", dismiss_promo, name="dismiss_promo"),
]
