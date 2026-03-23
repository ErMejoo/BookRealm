import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_realm_project.settings')

import django
django.setup()

from django.contrib.auth.models import User
from bookrealm.models import Genre, Book, Review, Follow, Wishlist
import random


Review.objects.all().delete()
Wishlist.objects.all().delete()
Follow.objects.all().delete()
Book.objects.all().delete()
Genre.objects.all().delete()
User.objects.filter(username__startswith='user').delete()

def populate():
    print("Populating database...")

    # --- Users ---
    usernames = ['user1', 'user2', 'user3', 'user4', 'user5']
    users = []
    for u in usernames:
        user, created = User.objects.get_or_create(username=u)
        if created:
            user.set_password('password123')
            user.save()
        users.append(user)
    print(f"Created {len(users)} users.")

    data = {
        'Fantasy': [
            {'title': "Harry Potter and the Philosopher's Stone", 'isbn':'9780747532699', 'description':'A young wizard begins his journey.', 'pages':223},
            {'title': 'The Hobbit', 'isbn':'9780261102217', 'description':'A hobbit goes on an adventure.', 'pages':310}
        ],
        'Sci-Fi': [
            {'title': 'Dune', 'isbn':'9780441013593', 'description':'A desert planet and political intrigue.', 'pages':412},
            {'title': 'Ender\'s Game', 'isbn':'9780812550702', 'description':'A child prodigy trains to fight aliens.', 'pages':324}
        ]
    }

    books = []
    for genre_name, book_list in data.items():
        genre, _ = Genre.objects.get_or_create(name=genre_name)
        for b in book_list:
            book, _ = Book.objects.get_or_create(
                isbn=b['isbn'],
                defaults={
                    'title': b['title'],
                    'description': b['description'],
                    'numPages': b['pages'],
                    'genre': genre,
                    'created_by': random.choice(users)
                }
            )
            books.append(book)
            print(f"Added book: {book.title} ({genre.name})")

    # --- Reviews ---
    for book in books:
        for _ in range(random.randint(1, 3)):  # 1-3 reviews per book
            user = random.choice(users)
            Review.objects.get_or_create(
                user=user,
                book=book,
                defaults={
                    'rating': random.randint(1, 5),
                    'comment_text': f"This is a review by {user.username}."
                }
            )

    # --- Follows ---
    for follower in users:
        following = random.choice([u for u in users if u != follower])
        Follow.objects.get_or_create(follower=follower, following=following)

    # --- Wishlists ---
    for user in users:
        book = random.choice(books)
        Wishlist.objects.get_or_create(user=user, book=book)

    print("Database population complete!")

if __name__ == '__main__':
    populate()