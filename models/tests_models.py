# created by R. Marabini on mar ago 17 14:11:42 CEST 2021
from decimal import Decimal
from django.test import TestCase

###################
# You may modify the following variables
from library.settings import BASE_DIR

pathToProject = BASE_DIR
from .models import Author as Author
from .models import Book as Book
from .models import User as User
from .models import Comment as Comment


# Please do not modify anything below this line
###################


class ModelTests(TestCase):
    """Test that populate  has been saved data properly
       require files XXXX.pkl stored in the same directory that manage.py"""

    def setUp(self):
        self.authorDict = {
            "first_name": 'Pedro',
            "last_name": 'Picapiedra',
        }
        self.bookDict = {
            "isbn": '1234567890123',
            "title": 'title_1',
            "price": Decimal(23.32),
            "path_to_cover_image": 'kk.jpg',
            "number_copies_stock": 23,
            "score": 9,
        }
        self.userDict = {
            "username": 'pmarmol',
            "password": 'troncomovil',
            "first_name": 'Pablo',
            "last_name": 'Marmol',
            "email": 'p.marmol@cantera.com',
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

    def test01_author(self):
        "Test author model"
        self.create_check(self.authorDict, Author)

    def test02_book(self):
        "Test book model with no authors"
        book = self.create_check(self.bookDict, Book)

        # Test book model with authors
        a1 = self.create_check(self.authorDict, Author)
        a2 = self.create_check(self.authorDict, Author)
        book.author.add(a1)
        book.author.add(a2)
        book.save()
        self.assertEqual(len(book.author.all()), 2)
        for author in book.author.all():
            self.assertEqual(self.authorDict['first_name'], author.first_name)
            self.assertEqual(self.authorDict['last_name'], author.last_name)
        # It should be possible to recover the books from Author objects
        bookA1 = a1.book_set.all()[0]  # get first book
        self.assertEqual(bookA1.pk, book.pk)  # compare primary keys

    def test03_comments(self):
        "test comments"
        # create and test user
        user = self.create_check(self.userDict, User)
        book = self.create_check(self.bookDict, Book)
        commentDict = {"book": book,
                       "user": user,
                       "msg": "this is a comment"}
        c1 = self.create_check(commentDict, Comment)
        self.assertEqual(user.pk, c1.user.pk)
        self.assertEqual(book.pk, c1.book.pk)

    def test04_databasename(self):
        # get data base name
        # this test will fail in heroku
        from django.db import connection
        db_name = connection.settings_dict['NAME']
        self.assertEqual(db_name, 'test_psi',
                         msg='this test will fail in heroku\n')
