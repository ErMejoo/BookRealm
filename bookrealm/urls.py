from django.urls import path
from bookrealm import views
app_name = 'BookRealm'
urlpatterns = [
    path('', views.home, name='home'),
    path('browse/', views.browse, name='browse'),
]