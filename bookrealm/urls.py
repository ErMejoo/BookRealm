from django.urls import path
from bookrealm import views
app_name = 'BookRealm'
urlpatterns = [
    path('', views.home, name='home'),
    path('browse/', views.browse, name='browse'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('chosen-author/<int:user_id>/', views.chosen_author, name='chosen_author'),
    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    path('wishlist/add/<int:book_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:book_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('chosen-book/<int:book_id>/', views.chosen_book, name='chosen_book'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('user_page/', views.user_page, name='user_page'),
    path('logout/', views.user_logout, name='logout'),
    path('contact_us', views.contact_us, name='contact_us'),
    path('my_books', views.my_books, name='my_books'),
    path('my_review', views.my_reviews, name='my_review'),
    path('publish_book', views.publish_book, name='publish_book'),
    path('review/add/<int:book_id>/', views.add_review, name='add_review'),
]