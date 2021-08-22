# code created by R. Marabini
import re
import glob
import os
from decimal import Decimal

from django.test import Client, TestCase  # , TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.test.utils import override_settings

###################
# You may modify the following variables

LOGIN_SERVICE = "login"
LOGOUT_SERVICE = "logout"
SIGNUP_SERVICE = "signup"
RESET_PASSWORD_SERVICE = "password_reset"
PASSWORD_RESET_CONFIRM_SERVICE = "password_reset_confirm"

PAGE_AFTER_LOGIN = "home"
PAGE_AFTER_LOGOUT = "home"
USER_SESSION_ID = "_auth_user_id"


SERVICE_DEF = {
     LOGIN_SERVICE: {
         "title": 'Log In',
         "pattern": r"Log In"
     },
}
# PLease do not modify anything below this line
###################

NUMBERUSERS = 5

class ServiceBaseTest(TestCase):
    """The database transaction that is being used by
    django.test.TestCase can be avoided by inheriting
    from django.test.TransactionTestCase instead of TestCase.
    Then the data will be visible in the database."""
    def setUp(self):
        User.objects.all().delete()
        self.usersList = []
        self.users = []
        for i in range(0, NUMBERUSERS):
            user = {"username": "user_%d" % i,
                    "password": "trampolin_%d" % i,
                    "first_name": "name_%d" % i,
                    "last_name": "last_%d" % i,
                    "email": "email_%d@gmail.com" % i}
            self.usersList.append(user)
            user = User.objects.create_user(**user)

            # store user id in list
            self.usersList[i]["id"] = user.id
            self.users.append(user)

        # create three clients so we can
        # test concurrency
        self.client1 = self.client
        self.client2 = Client()
        self.client3 = Client()

    # uncomment if you need to see the database
    # for debuging purposes
    # def tearDown(self):
    #    input(
    #        'Execution is paused and you can now inspect the database.\n'
    #        'Press return/enter key to continue:')

    @classmethod
    def decode(cls, txt):
        return txt.decode("utf-8")

    def validate_response(self, service, response, fail=False):
        definition = SERVICE_DEF[service]
        self.assertRegex(self.decode(response.content), definition["title"])
        if fail:
            # print(definition["patternfail"], self.decode(response.content))
            m = re.search(definition["patternfail"],
                          self.decode(response.content))
        else:
            # print(definition["pattern"], self.decode(response.content))
            m = re.search(definition["pattern"], self.decode(response.content))
        self.assertTrue(m)
        return m


class LogInOutServiceTests(ServiceBaseTest):

    def test01_log_page(self):
        "check log page but do not log in"
        # check that  no user is logged in
        # actually, ask the value of the session variable
        # USER_SESSION_ID. This variable should NOT
        # exist is nobody is logged in
        self.assertFalse(self.client1.session.get(USER_SESSION_ID, False))

        # call "login" service and check that "login" is in the title
        # LOGIN_SERVICE should match the label for your login url
        response = self.client1.get(reverse(LOGIN_SERVICE), follow=True)
        # The HTTP 200 code indicates that the request has succeeded
        self.assertEqual(response.status_code, 200)

        # check that the strings  SERVICE_DEF[LOGIN_SERVICE]
        # "title" and "pattern" are shown in login page
        self.validate_response(LOGIN_SERVICE, response)

        # so far we have just connected to the login page
        # but we have not log in so no user should be active
        self.assertFalse(self.client1.session.get(USER_SESSION_ID, False))

    def test02_log_in(self):
        "login and validate landing page"
        # no user logged in therefore, there should not be a
        # session variable named USER_SESSION_ID
        self.assertFalse(
            self.client1.session.get(USER_SESSION_ID, False))

        # log-in
        response = self.client1.post(reverse(LOGIN_SERVICE),
                                     self.usersList[0], follow=True)
        # after login session user should exists
        self.assertTrue(response.context['user'].is_active)

    def test03_log_in_several_users(self):
        """log in with 2 different users from two different
        clients/browsers. Then, request the home page and check
         the user name"""
        sessions = [
            {"client": self.client1, "user": self.usersList[0]},
            {"client": self.client2, "user": self.usersList[1]}
        ]
        # log in from two clients
        for session in sessions:
            session["client"].post(
                reverse(LOGIN_SERVICE), session["user"], follow=True)
        # connect to home (PAGE_AFTER_LOGIN) from two clients
        for session in sessions:
            response = session["client"].get(reverse(PAGE_AFTER_LOGIN),
                                             follow=True)
            self.assertTrue(response.context['user'].is_active)

    def test04_logout(self):
        "log in, then log out and test that user is not logged in"
        # check no user is logged in
        self.assertFalse(
            self.client1.session.get(USER_SESSION_ID, False))
        # log in
        self.client1.post(
            reverse(LOGIN_SERVICE), self.usersList[0], follow=True)

        # test user logged by checking user id
        self.assertEqual(Decimal(self.client1.session.get(USER_SESSION_ID)),
                         self.usersList[0]['id'])

        # logged out
        self.client1.get(reverse(LOGOUT_SERVICE), follow=True)

        # test user is logged out
        self.assertFalse(self.client1.session.get(USER_SESSION_ID, False))

    def test05_signup(self):
        # check  user does not exist
        i = NUMBERUSERS
        user = {"username": "user_%d" % i,
                "first_name": "name_%d" % i,
                "last_name": "last_%d" % i,
                "email": "email_%d@gmail.com" % i,
                "password": 'trekingff1',
                "password1": 'trekingff1',
                "password2": 'trekingff1'}
        self.assertFalse(
            User.objects.filter(username=user["username"]).exists())
        # send signup request
        self.client1.post(reverse(SIGNUP_SERVICE), user, follow=True)

        # login
        self.client1.post(reverse(LOGIN_SERVICE), user, follow=True)
        # print(self.decode(response.content))
        # check user login
        self.assertTrue(self.client1.session.get(USER_SESSION_ID, False))

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.filebased.EmailBackend')
    # see https://stackoverflow.com/questions/13848938/
    # django-test-framework-with-file-based-email-backend-server/
    # 15053970#15053970
    def test06_reset_password(self):
        "reset password if password forgotten using email"
        def utils_extract_reset_tokens(full_url):
            "find token in reset_password email"
            return re.findall(
                r"/([\w\-]+)",
                re.search(
                    r"^http\://.+$", full_url, flags=re.MULTILINE)[0])[3:5]

        from django.contrib.auth import authenticate
        # check this user exists
        user = authenticate(username=self.usersList[1]['username'],
                            password=self.usersList[1]['password'])

        # request reset password
        data = {'email': user.email}
        self.client1.post(
            reverse(RESET_PASSWORD_SERVICE), data, follow=True)
        # check file with email
        # open last file in directory settings.EMAIL_FILE_PATH
        # and extract tokens
        list_of_files = glob.glob(
            os.path.join(settings.EMAIL_FILE_PATH, '*.log'))
        latest_file = max(list_of_files, key=os.path.getctime)
        f = open(latest_file, "r")
        msg = f.read()
        f.close()
        # extract reset token from email
        uidb64, token = utils_extract_reset_tokens(msg)

        # define new password
        USER_NEW_PSW = 'tripillas'
        data = {
            "new_password1": USER_NEW_PSW,
            "new_password2": USER_NEW_PSW
        }
        # ask for reset password form
        # you can not go supply the new password without
        # calling the empty form first
        # see
        # https://stackoverflow.com/questions/50415700/
        # unable-to-create-an-integration-test-for-djangos-reset-password-flow
        self.client1.get(reverse(PASSWORD_RESET_CONFIRM_SERVICE,
                                 args=(uidb64, token)), follow=True)
        # send new password
        self.client1.post(
            reverse(PASSWORD_RESET_CONFIRM_SERVICE,
                    args=(uidb64, "set-password")),
            data,
            follow=True)
        # this authentication (old password) should fail
        user_new1 = authenticate(username=user.username,
                                 password=self.usersList[1]['password'])
        # this authentication (new password) should sucess
        user_new2 = authenticate(username=user.username,
                                 password=USER_NEW_PSW)
        self.assertIsNone(user_new1)
        self.assertEqual(user.username, user_new2.username)
