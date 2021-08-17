# created by R. Marabini on mar ago 17 14:11:42 CEST 2021
from django.test import TestCase
from catalog.management.commands.populate import Command

###################
# You may modify the following variables
from .models import Order as Order
from .models import OrderItem as OrderItem
from catalog.models import Book as Book
from library.settings import BASE_DIR
pathToProject = BASE_DIR
# Please do not modify anything below this line
###################


class ModelTests(TestCase):
    """Test that populate  has been saved data properly
       require files XXXX.pkl stored in the same directory that manage.py"""
    def setUp(self):
        self.populate = Command()
        self.populate.handle()

        self.OrderDict = {"first_name": 'Pedro',
                          "last_name": 'Picapiedra',
                          "email": 'p.picapiedra@cantera.com',
                          "address": 'Rocaplana 34',
                          "city": 'Piedradura',
                          "postal_code": '28049',
                          }

        book = Book.objects.first()
        self.OrderItemDict = {
            # order
            "book": book,
            "price": book.price,
            "quantity": 5,
        }

    def create_check(self, dictionary, ObjectClass):
        """ create an object of the class 'ObjectClass'
        using the dictionary. Then,
        check that all key-values in the
        dictionary are attributes in the object.
        return created object of class Object
        """
        # check that str function exists
        self.assertTrue(ObjectClass.__str__ is not object.__str__)
        # create object
        item = ObjectClass.objects.create(**dictionary)
        for key, value in dictionary.items():
            self.assertEqual(getattr(item, key), value)
        # execute __str__() so all the code in models.py is checked
        item.__str__()
        return item

    def test01_order(self):
        "Test order model"
        self.create_check(self.OrderDict, Order)

    def test02_orderItem(self):
        "Test orderitem model with no order"
        order = self.create_check(self.OrderDict, Order)
        self.OrderItemDict['order'] = order
        orderItem = self.create_check(self.OrderItemDict, OrderItem)

        # Test orderitem model with order
        # compare primary keys
        self.assertEqual(order.items.first().pk, orderItem.pk)

    def test03_order_total_cost(self):
        "TEST GET TOTAL COST"
        order = self.create_check(self.OrderDict, Order)
        self.OrderItemDict['order'] = order
        orderItem = self.create_check(self.OrderItemDict, OrderItem)

        # Test orderitem model with order
        self.assertEqual(order.get_total_cost(),
                         orderItem.quantity * orderItem.price)
