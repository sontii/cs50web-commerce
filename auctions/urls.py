from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.categories, name="categories"),
    path("categories_list/<str:category>", views.categories_list, name="categories_list"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("createlist", views.createlist, name="createlist"),
    path("", views.index, name="index"),
    path("<str:item>", views.item, name="item"),
   
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
