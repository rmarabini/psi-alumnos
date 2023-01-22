# created by R. Marabini on mar ago 17 14:11:42 CEST 2021

from django.urls import reverse
from time import sleep
from models.constants import QUESTION, ANSWER, LEADERBOARD
from .test_services import ServiceBaseTest

###################
# You may modify the following variables
from models.models import User as User
# from models.models import Questionnaire as Questionnaire
from models.models import Question as Question
# from models.models import Answer as Answer
from models.models import Game as Game
from models.models import Participant as Participant
# from models.models import Guess as Guess

# XXX_SERVICE is the alias of the service we want to tes
# XXX_KEY is the key, in the context diccionary, with the information
# that we want to pass to the template
# For example response.context['latest_questionnaire_list'] should contain
# the last five questionnaires created by the logged user

HOME_SERVICE = "home"
HOME_QUESTIONNAIRE_LIST_KEY = 'latest_questionnaire_list'

GAME_CREATE_SERVICE = "game-create"
GAME_UPDATE_PARTICIPANT_SERVICE = "game-updateparticipant"
GAME_UPDATE_PARTICIPANT_KEY = "gameupdateparticipant"

GAME_QUESTION_SERVICE = 'game-count-down'
GAME_ANSWER_SERVICE = 'game-count-down'
GAME_LEADERBOARD_SERVICE = 'game-count-down'

SESSION_STATE = 'game_state'

LOGIN_SERVICE = "login"
LOGOUT_SERVICE = "logout"

# PLease, do not modify anything below this line
###################


class ServiceTests2(ServiceBaseTest):

    def checkNoLogin(self, SERVICE, KEY, args=None, redirectLoginPage=True):
        """ check key is not in response if user is not logged"""
        # no login, therefore key KEY should be empty
        # first logout just in case
        self.client1.get(reverse(LOGOUT_SERVICE), follow=True)
        if args is None:
            response = self.client1.get(
                reverse(SERVICE), follow=True)
        else:
            response = self.client1.get(
                reverse(SERVICE, args=args), follow=True)
        # check no active user
        self.assertFalse(response.context['user'].is_active)
        # check no latest_questionnaire_list
        try:
            self.assertFalse(KEY in response.context)
        except Exception as e:
            pass
        # return should be login page
        if redirectLoginPage:
            self.assertIn('username', self.decode(response.content))

        return response

    def checkLogin(self, SERVICE, KEY, args=None):
        """ log in and check key is in response when user is logged"""
        # log-in
        response = self.client1.post(reverse(LOGIN_SERVICE),
                                     self.userDict, follow=True)
        # after login session user should exist
        self.assertTrue(response.context['user'].is_active)
        if args is None:
            response = self.client1.get(
                reverse(SERVICE), follow=True)
        else:
            response = self.client1.get(
                reverse(SERVICE, args=args), follow=True)

        # latest_questionnaire_list should exist
        if KEY != "DO_NOT_CHECK_KEY":
            self.assertTrue(KEY in response.context)
        return response

    def checkLoginSecondPart(self, SERVICE, args, kwargs=None):
        """ for those cases in which there is a confirmation page
        or a form and a post should follow a get request"""
        if kwargs is None:
            response = self.client1.post(
                reverse(SERVICE, args=args), follow=True)
        else:
            response = self.client1.post(
                reverse(SERVICE, args=args), kwargs, follow=True)

        return response


# GAME
    def test01_gameUpdateParticipant(self):
        "check how web page is update when participant join"
        from models.constants import WAITING
        id = self.questionnaire.id
        args = [str(id)]
        kwargs = {'state': WAITING}

        # no login, therefore key should be empty
        # response =
        self.checkNoLogin(GAME_CREATE_SERVICE, 'DO_NOT_CHECK_KEY', args=args)

        # login in,
        # response =
        self.checkLogin(GAME_CREATE_SERVICE, 'DO_NOT_CHECK_KEY', args=args)
        # print("RESPONSE", self.decode(response.content))
        game = Game.objects.first()
        self.assertEqual(game.questionnaire.id, int(id))
        self.assertEqual(game.state, kwargs["state"])
        # create participant and check that appear in the web page
        args = [str(game.publicId)]

        for id in range(10):
            Participant.objects.create(game=game, alias="alias_%d" % id)
            response = self.client1.get(
                reverse(GAME_UPDATE_PARTICIPANT_SERVICE), follow=True)
            for participant in range(id+1):
                print("checking participant", "alias_%d" % participant)
                self.assertNotEqual(
                    self.decode(
                        response.content).find("alias_%d" % participant), -1)
            sleep(0.1)

        # create new user, it will be used for login
        # and will not be the owner of the questionnaire
        self.userDict = {"username": 'b',
                         "password": 'b',
                         "first_name": 'b',
                         "last_name": 'b',
                         "email": 'b@bb.es'}
        user, created = User.objects.get_or_create(**self.userDict)
        if created:
            user.set_password(self.userDict['password'])
            user.save()
        self.user = user
        id = self.questionnaire.id
        args = [str(id)]
        self.checkLogin(GAME_CREATE_SERVICE, 'DO_NOT_CHECK_KEY', args=args)
        response = self.client1.get(
            reverse(GAME_UPDATE_PARTICIPANT_SERVICE), follow=True)

        self.assertNotEqual(
             self.decode(
                 response.content).find("does not belong to logged user"), -1)

    def test02_gameCountdown(self):
        """Check how the estate of game changes as we play.
        This test is very dependent on implementation, fill free to change it
        """
        from models.constants import WAITING

        id = self.questionnaire.id
        args = [str(id)]
        self.checkLogin(GAME_CREATE_SERVICE, 'DO_NOT_CHECK_KEY', args=args)
        game = Game.objects.first()
        self.assertEqual(game.state, WAITING)
        session = self.client1.session
        self.assertEqual(session[SESSION_STATE], WAITING)

        self.client1.get(reverse(GAME_QUESTION_SERVICE), follow=True)
        session = self.client1.session
        self.assertEqual(session[SESSION_STATE], QUESTION)

        self.client1.get(reverse(GAME_ANSWER_SERVICE), follow=True)
        session = self.client1.session
        self.assertEqual(session[SESSION_STATE], ANSWER)

        self.client1.get(reverse(GAME_QUESTION_SERVICE), follow=True)
        session = self.client1.session
        self.assertEqual(session[SESSION_STATE], QUESTION)

        self.client1.get(reverse(GAME_ANSWER_SERVICE), follow=True)
        session = self.client1.session
        self.assertEqual(session[SESSION_STATE], ANSWER)

        self.client1.get(reverse(GAME_QUESTION_SERVICE), follow=True)
        session = self.client1.session
        self.assertEqual(session[SESSION_STATE], LEADERBOARD)
