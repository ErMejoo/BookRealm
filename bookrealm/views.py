from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Follow, Wishlist, Book, Genre, Review
from django.db.models import Avg, Count
from datetime import datetime
from django.contrib import messages

# Create your views here.
def home(request):
    context_dict = {}
    top_books = (
        Book.objects.annotate(
            average_rating=Avg('review__rating'),
            number_reviews=Count('review')
        ).filter(number_reviews__gt=0).order_by('-average_rating')[:10]
    )
    # Book rating percentage
    for book in top_books:
        book.rating_percent = (book.average_rating or 0) * 20
        
    top_authors = (
        User.objects.annotate(
            average_rating=Avg('book__review__rating'),
            total_books=Count('book', distinct=True)
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
    response = render(request, 'bookrealm/contactUs.html')
    return response

def browse(request):
    response = render(request, 'bookrealm/browse.html')
    return response

def chosen_author(request, user_id):
    try:
        author = User.objects.get(id=user_id)
    except User.DoesNotExist:
        author = None
    is_following = False
    books = []
    avg_rating = 0
    total_books = 0
    if author:
        books = Book.objects.filter(created_by=author).annotate(
            average_rating=Avg('review__rating'),
            number_reviews=Count('review')
        )
        total_books = books.count()
        avg = books.aggregate(avg=Avg('review__rating'))['avg']
        avg_rating = round(avg, 1) if avg else 0
        if request.user.is_authenticated and request.user != author:
            is_following = Follow.objects.filter(
                follower=request.user, following=author
            ).exists()
    return render(request, "bookrealm/chosenAuthor.html", {
        'author': author,
        'is_following': is_following,
        'books': books,
        'total_books': total_books,
        'avg_rating': avg_rating,
    })
    
def chosen_book(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
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
    return render(request,
                  'bookrealm/chosenBook.html',
                  {'book': book, 'in_wishlist': in_wishlist, 'reviews': reviews,}
                  )

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
    return redirect(reverse('BookRealm:chosen_author', args=[user_id]))

@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = User.objects.get(id=user_id)
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    return redirect(reverse('BookRealm:chosen_author', args=[user_id]))

@login_required
def add_to_wishlist(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
        Wishlist.objects.get_or_create(user=request.user, book=book)
        messages.success(request, "Book added to the wishlist")
    except Book.DoesNotExist:
        pass
    return redirect(reverse('BookRealm:chosen_book', args=[book_id]))

@login_required
def remove_from_wishlist(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
        Wishlist.objects.filter(user=request.user, book=book).delete()
        messages.success(request, "Book removed from the wishlist")
    except Book.DoesNotExist:
        pass
    next_page = request.GET.get('next')
    if next_page == "book":
        return redirect(reverse("BookRealm:chosen_book", args=[book_id]))
    return redirect(reverse('BookRealm:view_wishlist'))

@login_required
def view_wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('book')
    return render(request, 'bookrealm/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('BookRealm:home'))

@login_required
def my_books(request):
    response = render(request, 'bookrealm/myBooks.html')
    return response

@login_required
def my_reviews(request):
    response = render(request, 'bookrealm/myReviews.html')
    return response

@login_required
def publish_book(request):
    response = render(request, 'bookrealm/publishBook.html')
    return response
