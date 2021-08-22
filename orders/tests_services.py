# created by R. Marabini on mar ago 17 14:11:42 CEST 2021

from django.test import TestCase
import time

from catalog.management.commands.populate import Command
from django.contrib.auth.models import User

###################
# You may modify the following variables
from catalog.models import Author as Author
from catalog.models import Book as Book
from catalog.models import Comment as Comment
from .models import Order as Order
from .models import OrderItem as OrderItem
from .forms import OrderCreateForm as OrderCreateForm
from .forms import CartAddBookForm as CartAddBookForm
from django.urls import reverse
from .cart import Cart

CARTADD_SERVICE = 'cart_add'
CARTLIST_SERVICE = 'cart_list'
CARTREMOVE_SERVICE = 'cart_remove'
LOGIN_SERVICE = "login"
ORDERSERVICE='order_create'
ORDERCOMPLETE = 'Your order has been successfully completed.'

FIRSTNAME = 'first_name'
LASTNAME = 'last_name'
EMAIL = 'email'
ADDRESS = 'address'
ZIP = 'postal_code'
CITY = 'city'
ORDERFORMERROR = u'This field is required.'
ORDERCREATE = "order_create"
# PLease do not modify anything below this line
###################


class ServiceBaseTest(TestCase):
    def setUp(self):
        self.client = self.client
        self.populate = Command()
        self.populate.handle()
        self.orderFormDict = {
            FIRSTNAME: 'Vilma',
            LASTNAME: 'Picapiedra',
            EMAIL: 'v.picapiedra@cantera.com',
            ADDRESS: 'Rocaplana 34',
            CITY: 'Piedradura',
            ZIP: '28049',
        }
        i=0
        self.user = {"username": "user_%d" % i,
                "password": "trampolin_%d" % i,
                "first_name": "name_%d" % i,
                "last_name": "last_%d" % i,
                "email": "email_%d@gmail.com" % i}
        User.objects.create_user(**(self.user))

    def tearDown(self):
        self.populate.cleanDataBase()

    @classmethod
    def decode(cls, txt):
        return txt.decode("utf-8")


class OrderTests(ServiceBaseTest):
    " test order form"
    def test00_blank_form(self):
        # check error if first_name is not provided
        form = OrderCreateForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors[FIRSTNAME],
                                    [ORDERFORMERROR])

    def test01_valid_form(self):
        form = OrderCreateForm(self.orderFormDict)
        if form.is_valid():
            self.assertTrue(True)
        else:
            print("form errors", form.errors)
            self.assertTrue(False)
            return
        self.assertTrue(form.is_valid())

        items = form.fields.keys()
        for k in items:
            self.assertEqual(form.cleaned_data[k], self.orderFormDict[k])

    def test02_order_defaults(self):
        form = OrderCreateForm(self.orderFormDict)
        order = form.save()
        self.assertFalse(order.paid)
        from django.utils import timezone
        now = timezone.localtime(timezone.now())
        old = timezone.localtime(order.created)
        # if we are going to change hour  12:59 -> 13:00 wait
        while old.minute > 58:
            time.sleep(10)
            old = timezone.localtime(order.created)
        self.assertEqual(old.year,now.year)
        self.assertEqual(old.month,now.month)
        self.assertEqual(old.day,now.day)
        self.assertEqual(old.hour,now.hour)

        old = timezone.localtime(order.created)
        self.assertEqual(old.year,now.year)
        self.assertEqual(old.month,now.month)
        self.assertEqual(old.day,now.day)
        self.assertEqual(old.hour,now.hour)


class CartTestServices(ServiceBaseTest):
    """test views related with shopping cart:
    # cart_list, add, remove
    """

    def test01_blank_form(self):
        form = CartAddBookForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'quantity': [u'This field is required.'],
        })

    def test02_valid_form(self):
        form = CartAddBookForm({
            'quantity': 7,
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['quantity'], 7)

    def test03_CartAddWeb(self):
        """ Add book to cart"""
        # create session so we can store the cart in it
        response = self.client.get(reverse('home'))
        # get book
        book = Book.objects.first()
        bookl = Book.objects.last()
        # copies of the book to be bought
        UNITS5 = 5
        UNITS3 = 3

        # log-in
        response = self.client.post(reverse(LOGIN_SERVICE),
                                    {'username': self.user['username'],
                                     'password': self.user['password']},
                                    follow=True)

        # after login session user should exists
        self.assertTrue(response.context['user'].is_active)

        #add items to the cart
        self.client.post(
            reverse(CARTADD_SERVICE, kwargs={'slug': book.slug}),
            data={'quantity': UNITS5}, follow=True)
        response = self.client.post(
            reverse(CARTADD_SERVICE, kwargs={'slug': bookl.slug}),
            data={'quantity': UNITS3}, follow=True)

        # get cart object
        request = response.wsgi_request
        cart = Cart(request).cart[str(book.id)]
        # test results
        self.assertEqual(cart['quantity'], UNITS5)
        self.assertEqual(cart['price'], book.price)
        # another book
        cart = Cart(request).cart[str(bookl.id)]
        # test results
        self.assertEqual(cart['quantity'], UNITS3)
        self.assertEqual(cart['price'], bookl.price)

    def test04_CartRemoveWeb(self):
        """ Add book to cart"""
        # create session so we can store the cart in it
        self.client.get(reverse('home'))
        # get book
        book = Book.objects.first()
        bookl = Book.objects.last()
        # copies of the book to be bought
        UNITS5 = 5
        UNITS3 = 3

        # log-in
        response = self.client.post(reverse(LOGIN_SERVICE),
                                    {'username': self.user['username'],
                                     'password': self.user['password']},
                                    follow=True)

        # after login session user should exists
        self.assertTrue(response.context['user'].is_active)

        #add items to the cart
        response = self.client.post(
            reverse(CARTADD_SERVICE, kwargs={'slug': book.slug}),
            data={'quantity': UNITS5}, follow=True)
        response = self.client.post(
            reverse(CARTADD_SERVICE, kwargs={'slug': bookl.slug}),
            data={'quantity': UNITS3}, follow=True)

        # remove item
        response = self.client.get(
            reverse(CARTREMOVE_SERVICE, kwargs={'slug': book.slug}),
            follow=True)
        # get cart dictionary
        request = response.wsgi_request
        cart = Cart(request).cart
        # chek removed book id not in dictionary
        self.assertFalse(str(book.id) in cart)
        self.assertTrue(str(bookl.id) in cart)

    def test05_CartListWeb(self):
        """ Add book to cart"""
        # create session so we can store the cart in it
        response = self.client.get(reverse('home'))
        # get book
        book = Book.objects.first()
        bookl = Book.objects.last()
        # copies of the book to be bought
        UNITS5 = 5
        UNITS3 = 3

        # log-in
        response = self.client.post(reverse(LOGIN_SERVICE),
                                    {'username': self.user['username'],
                                     'password': self.user['password']},
                                    follow=True)

        # after login session user should exists
        self.assertTrue(response.context['user'].is_active)

        #add items to the cart
        self.client.post(
            reverse(CARTADD_SERVICE, kwargs={'slug': book.slug}),
            data={'quantity': UNITS5}, follow=True)
        response = self.client.post(
            reverse(CARTADD_SERVICE, kwargs={'slug': bookl.slug}),
            data={'quantity': UNITS3}, follow=True)

        # get cart object
        request = response.wsgi_request
        cart = Cart(request).cart[str(book.id)]
        # test results
        self.assertEqual(cart['quantity'], UNITS5)
        self.assertEqual(cart['price'], book.price)
        # another book
        cart = Cart(request).cart[str(bookl.id)]
        # test results
        self.assertEqual(cart['quantity'], UNITS3)
        self.assertEqual(cart['price'], bookl.price)

        # List item
        response = self.client.get(reverse(CARTLIST_SERVICE),
            follow=True)
        # get cart dictionary
        request = response.wsgi_request
        cart = Cart(request).cart
        # chek removed book id not in dictionary
        response_txt = self.decode(response.content)
        self.assertIn(book.title, response_txt)
        self.assertIn(bookl.title, response_txt)


# you may need to modify cleanDataBase in populat
# so it deletes orders and orderitems
class OrderItemTests(ServiceBaseTest):
    """check that shopping cart is persisted in database"""
    def test01_persistcart(self):
        """ Check cart is persisted in orderitems"""
        # create session so we can store the cart in it
        response = self.client.get(reverse('home'))
        # get book
        book = Book.objects.first()
        bookl = Book.objects.last()
        # copies of the book to be bought
        UNITS5 = 5
        UNITS3 = 3

        # log-in
        response = self.client.post(reverse(LOGIN_SERVICE),
                                    {'username': self.user['username'],
                                     'password': self.user['password']},
                                    follow=True)

        # after login session user should exists
        self.assertTrue(response.context['user'].is_active)

        #add items to the cart
        self.client.post(
            reverse(CARTADD_SERVICE, kwargs={'slug': book.slug}),
            data={'quantity': UNITS5}, follow=True)
        response = self.client.post(
            reverse(CARTADD_SERVICE, kwargs={'slug': bookl.slug}),
            data={'quantity': UNITS3}, follow=True)

        # get cart object
        request = response.wsgi_request
        cart = Cart(request).cart

        # checkout
        response = self.client.post(
            reverse(ORDERSERVICE),
            data = self.orderFormDict,
            follow=True
        )
        self.assertIn(ORDERCOMPLETE, self.decode(response.content))
        twoSlug = ""
        for orderitem in OrderItem.objects.all():
            twoSlug += orderitem.book.slug
        self.assertIn(book.slug, twoSlug)
        self.assertIn(bookl.slug, twoSlug)