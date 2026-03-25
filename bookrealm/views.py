from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Follow, Wishlist, Book, Genre, Review, UserProfile
from django.db.models import Avg, Count
from datetime import datetime
from django.contrib import messages
from django.http import JsonResponse

# Create your views here.
def _get_safe_next_url(request):
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return None


def home(request):
    context_dict = {}
    top_books = (
        Book.objects.annotate(
            avg_rating=Avg('review__rating'),
            number_reviews=Count('review')
        ).filter(number_reviews__gt=0).order_by('-avg_rating')[:10]
    )
    # Book rating percentage
    for book in top_books:
        book.rating_percent = (book.avg_rating or 0) * 20
        
    top_authors = (
        User.objects.select_related('userprofile')
        .annotate(
            average_rating=Avg('books__review__rating'),
            total_books=Count('books', distinct=True)
        ).filter(total_books__gt=0).order_by('-average_rating')[:10]
    )
    # Author rating percentage
    for author in top_authors:
        author.rating_percent = (author.average_rating or 0) * 20
    genres = Genre.objects.all()
    context_dict['top_books'] = top_books
    context_dict['top_authors'] = top_authors
    context_dict['genres'] = genres
    return render(request, 'bookrealm/home.html', context_dict)

def contact_us(request):
    return render(request, 'bookrealm/contactUs.html')

def browse(request):
    books = Book.objects.all().annotate(
        avg_rating=Avg('review__rating'),
        num_likes=Count('wishlist_items'),
        number_reviews=Count('review')
    )

    genre_id = request.GET.get('genre')
    selected_sort = request.GET.get('sort')
    query = request.GET.get('q')

    if query:
        books = books.filter(title__icontains=query)

    if genre_id:
        books = books.filter(genre_id=genre_id)

    if selected_sort == 'rating':
        books = books.order_by('-avg_rating')
    elif selected_sort == 'newest':
        books = books.order_by('-created_at')
    else:
        books = books.order_by('title')

    genres = Genre.objects.all()

    return render(request, 'bookrealm/browse.html', {
        'books': books,
        'genres': genres,
        'selected_genre': genre_id,
        'selected_sort': selected_sort,
        'query': query,
    })
    

def chosen_author(request, user_id):
    try:
        author = User.objects.get(id=user_id)
        author_profile = UserProfile.objects.get(user=author)
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        return render(request, "bookrealm/chosenAuthor.html", {'author': None})
    is_following = False
    books = Book.objects.filter(created_by=author).annotate(
        avg_rating=Avg('review__rating'),
        number_reviews=Count('review')
    )
    reviews = Review.objects.filter(book__created_by=author)
    avg_aggregate = reviews.aggregate(avg=Avg('rating'))  
    avg_rating = avg_aggregate['avg'] if avg_aggregate['avg'] is not None else 0
    total_books = books.count()
    rating_percent = avg_rating * 20
    if request.user.is_authenticated and request.user != author:
        is_following = Follow.objects.filter(
            follower=request.user, following=author
        ).exists()
    return render(request, "bookrealm/chosenAuthor.html", {
        'author': author,
        'author_profile': author_profile,
        'is_following': is_following,
        'books': books,
        'total_books': total_books,
        'avg_rating': avg_rating,
        'rating_percent': rating_percent,
    })
def chosen_book(request, book_id):
    try:
        book = Book.objects.annotate(
        average_rating=Avg('review__rating'),
        review_count=Count('review')
        ).get(id=book_id)
        book.rating_percent = (book.average_rating or 0) * 20
    except Book.DoesNotExist:
        book = None
    in_wishlist = False
    if request.user.is_authenticated and book:
        in_wishlist = Wishlist.objects.filter(user=request.user, book=book).exists()
    reviews = []
    if book:
        reviews = book.review_set.select_related('user').order_by('-created_at')
        if request.user.is_authenticated:
            in_wishlist = Wishlist.objects.filter(
                user=request.user, book=book
            ).exists()
    user_review = None
    if request.user.is_authenticated and book:
        user_review = Review.objects.filter(user=request.user, book=book).first()
    return render(request, 'bookrealm/chosenBook.html', {
        'book': book,
        'in_wishlist': in_wishlist,
        'reviews': reviews,
        'user_review': user_review,
    })

@login_required
def add_review(request, book_id):
    if request.method == "POST":
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return redirect('BookRealm:home')
        
        rating = request.POST.get('rating')
        comment = request.POST.get('comment_text')

        if rating and comment:
            Review.objects.update_or_create(
                user=request.user,
                book=book,
                defaults={
                    'rating': int(rating),
                    'comment_text': comment
                }
            )
            messages.success(request, "Review added successfully!")

        return redirect(reverse('BookRealm:chosen_book', args=[book_id]))
    
    return redirect('BookRealm:home')

@login_required
def follow_user(request, user_id):
    user_to_follow = User.objects.get(id=user_id)
    Follow.objects.get_or_create(follower=request.user, following=user_to_follow)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'followed'})
    return redirect(reverse('BookRealm:chosen_author', args=[user_id]))

@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = User.objects.get(id=user_id)
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'unfollowed'})
    return redirect(reverse('BookRealm:chosen_author', args=[user_id]))

@login_required
def add_to_wishlist(request, book_id):
    if request.method == "POST":
        try:
            book = Book.objects.get(id=book_id)
            Wishlist.objects.get_or_create(user=request.user, book=book)

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'added'})
            
        except Book.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return redirect(reverse('BookRealm:chosen_book', args=[book_id]))

@login_required
def remove_from_wishlist(request, book_id):
    if request.method == "POST":
        try:
            book = Book.objects.get(id=book_id)
            Wishlist.objects.filter(user=request.user, book=book).delete()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'removed'})
        except Book.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return redirect(reverse('BookRealm:view_wishlist'))

@login_required
def view_wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('book')
    return render(request, 'bookrealm/wishlist.html', {'wishlist_items': wishlist_items})

def register(request):
    next_url = _get_safe_next_url(request)
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        account_type = request.POST.get('account_type')
        profile_picture = request.FILES.get('picture')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('BookRealm:register')
        user = User.objects.create_user(username=username, email=email, password=password)
        is_author = True if account_type == 'author' else False
        UserProfile.objects.create(
            user=user, 
            is_author=is_author,
            picture=profile_picture
        )
        login(request, user)
        messages.success(request, f"Account created successfully. Welcome, {user.username}.")
        return redirect(next_url or 'BookRealm:home')
    return render(request, 'bookrealm/register.html', {'next': next_url})

def user_login(request):
    next_url = _get_safe_next_url(request)
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}.")
            return redirect(next_url or 'BookRealm:home')
        else:
            messages.error(request, "Invalid login details.")
    return render(request, 'bookrealm/login.html', {'next': next_url})

@login_required
def user_page(request):
    context_dict = {}
    try:
        profile = UserProfile.objects.get(user=request.user)
        context_dict['profile'] = profile
        
        followed_authors = Follow.objects.filter(follower=request.user).select_related('following', 'following__userprofile')
        context_dict['followed_authors'] = followed_authors
        
        if profile.is_author:
            my_books = Book.objects.filter(created_by=request.user).annotate(
                avg_rating=Avg('review__rating'),
                number_reviews=Count('review')
            )
            context_dict['my_books'] = my_books
            
    except UserProfile.DoesNotExist:
        pass

    return render(request, 'bookrealm/user-page.html', context_dict)

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect(reverse('BookRealm:home'))

@login_required
def my_reviews(request):
    response = render(request, 'bookrealm/myReviews.html')
    return response

@login_required
def publish_book(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        numPages = request.POST.get('numPages')
        isbn = request.POST.get('isbn')
        genre_id = request.POST.get('genre')
        cover = request.FILES.get('cover_image')
        if title:
            genre = Genre.objects.get(id=genre_id) if genre_id else None
            Book.objects.create(
                title=title,
                description=description,
                numPages=numPages,
                isbn=isbn,
                genre=genre,
                created_by=request.user,
                cover_image=cover
            )
            messages.success(request, "Book published successfully!")
            return redirect('BookRealm:browse')
    genres = Genre.objects.all()
    return render(request, 'bookrealm/publishBook.html', {'genres': genres})

