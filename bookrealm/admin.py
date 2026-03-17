from django.contrib import admin
from .models import Genre, Book, Review, Follow, Wishlist

# Register models so they appear in Django admin
admin.site.register(Genre)
admin.site.register(Book)
admin.site.register(Review)
admin.site.register(Follow)
admin.site.register(Wishlist)
