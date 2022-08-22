# created by R. Marabini on mar ago 17 14:11:42 CEST 2021

from django.test import Client, TestCase
from django.urls import reverse

from .management.commands.populate import Command

###################
# You may modify the following variables
from .models import Author as Author
from .models import Book as Book
from .models import Comment as Comment

DETAIL_SERVICE = "detail"
SEARCH_SERVICE = "search"
SEARCH_TITLE = "Search"

SERVICE_DEF = {DETAIL_SERVICE: {
        "title": "",
    },
    SEARCH_SERVICE: {
        "title": SEARCH_TITLE,
    },
}
# PLease do not modify anything below this line
###################


class ServiceBaseTest(TestCase):
    def setUp(self):
        self.client1 = self.client
        self.client2 = Client()
        self.client3 = Client()
        self.populate = Command()
        self.populate.handle()

    def tearDown(self):
        self.populate.cleanDataBase()

    @classmethod
    def decode(cls, txt):
        return txt.decode("utf-8")


class CatalogServiceTests(ServiceBaseTest):

    def test00_populate_imports(self):
        # check number of items to be created
        self.assertGreater(self.populate.NUMBERBOOKS, 5)
        self.assertGreater(self.populate.NUMBERCOMMENTS, 5)
        self.assertGreater(self.populate.NUMBERAUTHORS, 5)

    def test01_list(self):
        " check that NUMBERBOOKS books have been generated"
        # get all books
        books = Book.objects.all()
        self.assertEqual(len(books), self.populate.NUMBERBOOKS,
                         "wrong number of books")

    def test02_details(self):
        "check detail page"
        # get all books
        books = Book.objects.all()
        # get response with all book title
        # check all books
        for book in books:
            response = self.client1.get(
                reverse(DETAIL_SERVICE, kwargs={'slug': book.slug}),
                follow=True)
            response_txt = self.decode(response.content)
            self.assertFalse(response_txt.find(book.title) == -1)
            self.assertFalse(response_txt.find(str(book.price)) == -1)
            authors = book.author.all()
            self.assertGreater(len(authors), 0,
                               "number of author must be greater than 0")
            # check authors for this book
            for author in authors:
                self.assertFalse(response_txt.find(author.first_name) == -1)
                self.assertFalse(response_txt.find(author.last_name) == -1)
        # check comments
        comments = Comment.objects.all()
        self.assertEqual(len(comments), self.populate.NUMBERCOMMENTS,
                         "wrong number of comments")
        for comment in comments:
            book = comment.book
            response = self.client1.get(reverse(DETAIL_SERVICE,
                                                kwargs={'slug': book.slug}),
                                        follow=True)
            # check comment is in corresponding detail page
            response_txt = self.decode(response.content)
            self.assertFalse(response_txt.find(comment.msg) == -1)

    def test03_pagination_is_five(self):
        searchString = 'a'
        response = self.client1.get(
            reverse(SEARCH_SERVICE) + '?q=%s' % searchString, follow=True)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['book_list']), 5)

    def test04_pagination_get_second_page(self):
        # Get second page. This will only work if
        # standard django pagination is used
        searchString = 'a'
        response = self.client1.get(
            reverse(SEARCH_SERVICE) + '?q=%s&page=2' % searchString,
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['book_list']), 5)

    def test05_search(self):
        """Get all pages with the result of search and check
        the books are the right ones"""
        searchString = 'a'
        # there are more efficient ways to do these 3 queries
        aaBooks = Book.objects.filter(title__icontains=searchString)
        aaAuthor1 = Author.objects.filter(first_name__icontains=searchString)
        aaAuthor2 = Author.objects.filter(last_name__icontains=searchString)

        response = self.client1.get(
            reverse(SEARCH_SERVICE) + '?q=%s' % searchString, follow=True)
        response_txt = self.decode(response.content)
        for i in range(int(response.context['paginator'].num_pages)+1):
            response = self.client1.get(
                reverse(SEARCH_SERVICE) + '?q=%s&page=%d' % (searchString, i),
                follow=True)
            response_txt += self.decode(response.content)

        for book in aaBooks:
            self.assertIn(book. title, response_txt)
        for author in aaAuthor1:
            for book in author.book_set.all():
                self.assertIn(book.title, response_txt)
        for author in aaAuthor2:
            for book in author.book_set.all():
                self.assertIn(book.title, response_txt)

    def test06_search_case(self):
        "check that the search is no case sensitive"
        searchString = 'b'
        SearchString = 'B'
        response = self.client1.get(
            reverse(SEARCH_SERVICE) + '?q=%s' % searchString, follow=True)
        Response = self.client2.get(
            reverse(SEARCH_SERVICE) + '?q=%s' % SearchString, follow=True)
        self.assertEqual(response.context['paginator'].count,
                         Response.context['paginator'].count)
