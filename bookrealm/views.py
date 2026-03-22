from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Follow, Wishlist, Book, Genre
from django.db.models import Avg, Count
from datetime import datetime
from django.contrib import messages

# Create your views here.
def home(request):
    context_dict = {}
    top_books = (
        Book.objects.annotate(average_rating=Avg('review__rating'),number_reviews=Count('review')).filter(number_reviews__gt=0).order_by('-average_rating')[:10]
    )
    top_authors = (
        User.objects.annotate(
            average_rating=Avg('books__review__rating'),
            total_books=Count('books')
        ).filter(total_books__gt=0).order_by('-average_rating')[:10]
    )
    genres = Genre.objects.all()
    context_dict['top_books'] = top_books
    context_dict['top_authors'] = top_authors
    context_dict['genres'] = genres
    response = render(request, 'bookrealm/home.html', context_dict)
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
    if request.user.is_authenticated and author and request.user != author:
        is_following = Follow.objects.filter(follower=request.user, following=author).exists()
    return render(request, "bookrealm/chosenAuthor.html", {'author': author, 'is_following': is_following})

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


    
