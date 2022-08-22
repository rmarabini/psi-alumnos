# created by R. Marabini
# Uncomment if you want to run tests in transaction mode with a final rollback
from django.test import TestCase
#uncomment this if you want to keep data after running tests
#from unittest import TestCase

from django.urls import reverse
from django.test import Client
from catalog.models import Book
from django.conf import settings
from .cart import Cart
from decimal import Decimal
from catalog.management.commands.populate import Command

class CartTest(TestCase):
    def setUp(self):
        # fill database
        self.populate = Command()
        self.populate.handle()
        self._client = Client()

    def test01_CartAdd(self):
        """ Add book to cart"""
        # create session so we can store the cart in it
        response = self._client.get(reverse('home'))
        request = response.wsgi_request

        # get book
        books = Book.objects.all()
        # create cart
        UNITS5 = 5
        UNITS3 = 3
        cart = Cart(request)

        # add items to the cart
        book0 = books.first()
        cart.add(book0, quantity=UNITS5)
        price = request.session[settings.CART_SESSION_ID][str(book0.id)]['price']
        quantity = request.session[settings.CART_SESSION_ID][str(book0.id)]['quantity']
        # check the values are stored in the session
        self.assertEquals(book0.price, Decimal(price))
        self.assertEquals(UNITS5, quantity)

        # add more items
        cart.add(book0, quantity=UNITS3)
        quantity = request.session[settings.CART_SESSION_ID][str(book0.id)]['quantity']
        self.assertEquals(UNITS5 + UNITS3, quantity)

    def test02_CartRemove(self):
        """ Remove book from cart"""
        # create session so we can store the cart in it
        response = self._client.get(reverse('home'))
        request = response.wsgi_request

        # get book
        books = Book.objects.all()
        # create cart
        UNITS5 = 5
        cart = Cart(request)

        # add items to the cart
        book0 = books.first()
        book1 = books[1]
        cart.add(book0, quantity=UNITS5)
        cart.add(book1, quantity=UNITS5)
        # check quantity
        quantity0 = request.session[settings.CART_SESSION_ID][
            str(book0.id)]['quantity']
        quantity1 = request.session[settings.CART_SESSION_ID][
            str(book1.id)]['quantity']
        self.assertEquals(UNITS5, quantity0)
        self.assertEquals(UNITS5, quantity1)
        # remove book
        cart.remove(book0)
        # check quantity
        self.assertFalse(str(book0.id) in request.session[settings.CART_SESSION_ID])
        self.assertTrue(str(book1.id) in request.session[settings.CART_SESSION_ID])

    def test03_CartLen(self):
        "number of books in cart"
        # create session so we can store the cart in it
        response = self._client.get(reverse('home'))
        request = response.wsgi_request

        # get book
        books = Book.objects.all()
        # create cart
        UNITS5 = 5
        UNITS3 = 3
        cart = Cart(request)

        # add items to the cart
        book0 = books.first()
        book1 = books[1]
        cart.add(book0, quantity=UNITS5)
        cart.add(book1, quantity=UNITS3)
        size = len(cart)
        self.assertEqual(UNITS5 + UNITS3, size)


    def test04_CartTotalPrice(self):
        # CREATE SESSION
        # create session so we can store the cart in it
        response = self._client.get(reverse('home'))
        request = response.wsgi_request

        # get book
        books = Book.objects.all()
        # create cart
        UNITS5 = 5
        UNITS3 = 5
        cart = Cart(request)

        # add items to the cart
        book0 = books.first()
        book1 = books[1]
        cart.add(book0, quantity=UNITS5)
        cart.add(book1, quantity=UNITS3)

        totalPrice = cart.get_total_price()
        quantity0 = request.session[settings.CART_SESSION_ID][
            str(book0.id)]['quantity']
        quantity1 = request.session[settings.CART_SESSION_ID][
            str(book1.id)]['quantity']
        _totalPrice = book0.price * quantity0 + \
                      book1.price * quantity1
        self.assertEqual(totalPrice, _totalPrice)
