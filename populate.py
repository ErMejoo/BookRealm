import os
import random
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_realm_project.settings')
django.setup()

from django.contrib.auth.models import User
from bookrealm.models import Genre, Book, Review, Follow, Wishlist, UserProfile

# Returns a list of all image paths in a given folder within the project root
def get_image_paths(folder_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.join(base_dir, folder_name)
    if os.path.exists(target_path):
        return [os.path.join(target_path, f) for f in os.listdir(target_path) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    return []

def populate():
    print(" Starting Database Population")
    # Cleaning old data
    print("Cleaning database...")
    Review.objects.all().delete()
    Wishlist.objects.all().delete()
    Follow.objects.all().delete()
    Book.objects.all().delete()
    UserProfile.objects.all().delete()
    Genre.objects.all().delete()
    User.objects.filter(username__in=['JK_Rowling', 'JRR_Tolkien', 'Frank_Herbert', 'Agatha_Christie', 'Orson_Scott_Card']).delete()

    all_profile_pics = get_image_paths('media/profile_images')
    all_cover_pics = get_image_paths('media/covers')
    profile_src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media/profile_images')
    cover_src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media/covers')
    
    authors_info = [
        {'username': 'JK_Rowling', 'first': 'Joanne', 'last': 'Rowling'},
        {'username': 'JRR_Tolkien', 'first': 'J.R.R.', 'last': 'Tolkien'},
        {'username': 'Frank_Herbert', 'first': 'Frank', 'last': 'Herbert'},
        {'username': 'Orson_Scott_Card', 'first': 'Orson Scott', 'last': 'Card'},
        {'username': 'Agatha_Christie', 'first': 'Agatha', 'last': 'Christie'},     
    ]
    
    users_dict = {}
    for data in authors_info:
        user = User.objects.create_user(
            username=data['username'], 
            password='password123',
            first_name=data['first'],
            last_name=data['last']    
        )  
        profile = UserProfile.objects.create(
            user=user, 
            is_author= True,
            bio=f"Official profile of {data['first']} {data['last']}"
        )
        
        # Look for a file named exactly after the username (e.g., user1.jpg)
        specific_pic = None
        for ext in ['.jpg', '.jpeg', '.png']:
            potential_file = os.path.join(profile_src_dir, f"{data['username']}{ext}")
            if os.path.exists(potential_file):
                specific_pic = potential_file
                break
        
        # If specific pic not found, pick a random one from the folder
        pic_to_use = specific_pic or (random.choice(all_profile_pics) if all_profile_pics else None)

        if pic_to_use:
            with open(pic_to_use, 'rb') as f:
                profile.picture.save(f"{data['username']}.jpg", File(f), save=True)
                print(f"Assigned image to user: {data['username']}")
        
        users_dict[data['username']] = user

    # Genres and Books
    data = {
        'Fantasy': [
            {'title': "Harry Potter and the Philosopher's Stone", 'isbn':'9780008386819', 'pages':223, 'author': 'JK_Rowling'},
            {'title': 'The Hobbit', 'isbn':'9780008386820', 'pages':310, 'author': 'JRR_Tolkien'},
            {'title': 'The Silmarillion', 'isbn': '9780008386821', 'pages': 365, 'author': 'JRR_Tolkien'},
        ],
        'Sci-Fi': [
            {'title': 'Dune', 'isbn':'9780008386822', 'pages':412, 'author': 'Frank_Herbert'},
            {'title': 'Ender\'s Game', 'isbn':'9780008386823', 'pages':324, 'author': 'Orson_Scott_Card'},
        ],
        'Mystery': [
            {'title': 'Murder on the Orient Express', 'isbn': '9780008386824', 'pages': 289, 'author': 'Agatha_Christie'},
            {'title': 'Death on the Nile', 'isbn': '9780008386825', 'pages': 336, 'author': 'Agatha_Christie'},
        ]
    }

    books_list = []
    for genre_name, books in data.items():
        genre, _ = Genre.objects.get_or_create(name=genre_name)
        for b in books:
            creator = users_dict[b['author']]
            book = Book.objects.create(
                isbn=b['isbn'],
                title=b['title'],
                numPages=b['pages'],
                genre=genre,
                created_by=creator,
                description=f"An amazing {genre_name} book written by {creator.username}."
            )

            # Look for a file named exactly after the ISBN (e.g., 9780008386825.jpg)
            specific_cover = None
            for ext in ['.jpg', '.jpeg', '.png']:
                potential_cover = os.path.join(cover_src_dir, f"{b['isbn']}{ext}")
                if os.path.exists(potential_cover):
                    specific_cover = potential_cover
                    break
            
            cover_to_use = specific_cover or (random.choice(all_cover_pics) if all_cover_pics else None)

            if cover_to_use:
                with open(cover_to_use, 'rb') as f:
                    book.cover_image.save(f"cover_{b['isbn']}.jpg", File(f), save=True)
            
            books_list.append(book)
            print(f"Added book: {book.title}")

    # Reviews, Follows and Wishlist
    print("Finalizing relationships (Reviews, Follows, Wishlists)...")
    all_users = list(users_dict.values())
    for book in books_list:
        for _ in range(random.randint(1, 2)):
            reviewer = random.choice(all_users)
            Review.objects.create(
                user=reviewer, book=book, 
                rating=random.randint(4, 5),
                comment_text=f"Impressive work by {book.created_by.username}!"
            )

    for u in all_users:
        # Follow a random user
        target = random.choice([user for user in all_users if user != u])
        Follow.objects.get_or_create(follower=u, following=target)
        # Random wishlist item
        Wishlist.objects.get_or_create(user=u, book=random.choice(books_list))

    print("\n--- Population Complete! Check your 'media/' folder. ---")

if __name__ == '__main__':
    populate()