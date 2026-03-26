from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Book, Review, Wishlist


class BookModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.book = Book.objects.create(
            isbn='1234567890123',
            title='Test Book',
            description='Test description',
            numPages=100,
            created_by=self.user
        )

    def test_book_creation(self):
        self.assertEqual(self.book.title, 'Test Book')
        self.assertEqual(self.book.numPages, 100)

    def test_review_creation(self):
        review = Review.objects.create(
            user=self.user,
            book=self.book,
            rating=5,
            comment_text="Great book!"
        )

        self.assertEqual(review.book, self.book)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.rating, 5)


class ViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_home_page(self):
        response = self.client.get(reverse('BookRealm:home'))
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        login = self.client.login(username='testuser', password='12345')
        self.assertTrue(login)


class AddReviewViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.book = Book.objects.create(
            isbn='1234567890123',
            title='Test Book',
            description='Test',
            numPages=100,
            created_by=self.user
        )

    def test_add_review(self):
        self.client.login(username='testuser', password='12345')

        response = self.client.post(
            reverse('BookRealm:add_review', args=[self.book.id]),
            {
                'rating': 5,
                'comment_text': 'Nice book'
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 1)


class RatingLogicTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create(username='testuser1')
        self.user2 = User.objects.create(username='testuser2')
        self.book = Book.objects.create(
            isbn='1234567890123',
            title='Test Book',
            description='Test',
            numPages=100,
            created_by=self.user1
        )

    def test_average_rating(self):
        Review.objects.create(user=self.user1, book=self.book, rating=4, comment_text="Good")
        Review.objects.create(user=self.user2, book=self.book, rating=2, comment_text="Bad")

        reviews = Review.objects.filter(book=self.book)
        avg = sum(r.rating for r in reviews) / reviews.count()

        self.assertEqual(avg, 3)


class EdgeCaseTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.book = Book.objects.create(
            isbn='9999999999999',
            title='Empty Book',
            description='No reviews yet',
            numPages=100,
            created_by=self.user
        )

    def test_no_reviews_avg(self):
        reviews = Review.objects.filter(book=self.book)
        if reviews.count() == 0:
            avg = 0
        else:
            avg = sum(r.rating for r in reviews) / reviews.count()

        self.assertEqual(avg, 0)


class PermissionTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.book = Book.objects.create(
            isbn='8888888888888',
            title='Secure Book',
            description='Test',
            numPages=100,
            created_by=self.user
        )

    def test_add_review_without_login(self):
        response = self.client.post(
            reverse('BookRealm:add_review', args=[self.book.id]),
            {'rating': 5, 'comment_text': 'Test'}
        )

        self.assertEqual(response.status_code, 302)


class WishlistTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.book = Book.objects.create(
            isbn='7777777777777',
            title='Wishlist Book',
            description='Test',
            numPages=100,
            created_by=self.user
        )

    def test_add_to_wishlist(self):
        self.client.login(username='testuser', password='12345')

        response = self.client.post(
            reverse('BookRealm:add_to_wishlist', args=[self.book.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Wishlist.objects.count(), 1)