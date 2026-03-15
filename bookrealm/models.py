from django.db import models
from django.contrib.auth.models import User


# class WishlistItem(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
#     book = models.ForeignKey('Book', on_delete=models.CASCADE, related_name="wishlist_items")
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('user', 'book')

#     def __str__(self):
#         return f"{self.user.username} wishlisted {self.book}"


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
    
