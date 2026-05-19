from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='blog-home'),
    path('about/', views.about, name='blog-about'),
    path('search/', views.search, name='blog-search'),
    path('reading-list/', views.reading_list, name='reading-list'),
    path('category/<slug:slug>/', views.category_posts, name='category-posts'),
    path('tag/<slug:slug>/', views.tag_posts, name='tag-posts'),
    path('post/new/', views.PostCreateView.as_view(), name='post-create'),
    path('post/<slug:slug>/', views.post_detail, name='post-detail'),
    path('post/<slug:slug>/update/', views.PostUpdateView.as_view(), name='post-update'),
    path('post/<slug:slug>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    path('post/<slug:slug>/toggle-read/', views.toggle_read, name='toggle-read'),
    path('post/<slug:slug>/toggle-save/', views.toggle_save, name='toggle-save'),
]
