# created by R. Marabini on mar ago 17 14:11:42 CEST 2021

from django.test import TestCase
import time

from catalog.management.commands.populate import Command

###################
# You may modify the following variables
from catalog.models import Author as Author
from catalog.models import Book as Book
from catalog.models import Comment as Comment
from .models import Order as Order
from .models import OrderItem as OrderItem
from .forms import OrderCreateForm as OrderCreateForm

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

    def tearDown(self):
        self.populate.cleanDataBase()

    @classmethod
    def decode(cls, txt):
        return txt.decode("utf-8")


class OrderTests(ServiceBaseTest):

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
        from django.utils import timezone
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
