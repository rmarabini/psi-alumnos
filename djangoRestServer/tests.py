from ast import alias
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from models.models import Game, Guess, Participant, User, Questionnaire, Question, Answer
from rest_framework.reverse import reverse
import json
from models.constants import QUESTION
###################
# You may modify the following variables

GAME_DETAIL = "game-detail"
GUESS_ERROR = 'wait until the question is shown'
GUESS_DELETE_ERROR = "Authentication credentials were not provided."
GUESS_UPDATE_ERROR = "Authentication credentials were not provided."
GUESS_CREATE_ERROR = "Authentication credentials were not provided."
PARTICIPANT_UPDATE_ERROR = "Authentication credentials were not provided."
PARTICIPANT_DELETE_ERROR = "Authentication credentials were not provided."
PARTICIPANT_LIST_ERROR = "Authentication credentials were not provided."

# PLease do not modify anything below this line
###################




class RestTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # user
        self.userDict = {"username": 'a',
                         "password": 'a',
                         "first_name": 'a',
                         "last_name": 'a',
                         "email": 'a@aa.es'
                         }
        user, created = User.objects.get_or_create(**self.userDict)
        if created:
            user.set_password(self.userDict['password'])
            user.save()
        self.user = user

        # questionnaire
        self.questionnaireDict = {"title": 'questionnaire_title',
                                  "user": self.user
                                  }
        self.questionnaire = Questionnaire.objects.get_or_create(
            **self.questionnaireDict)[0]

        # question
        self.questionDict = {"question": 'this is a question',
                             "questionnaire": self.questionnaire,
                             }
        self.question = Question.objects.get_or_create(**self.questionDict)[0]

        # question2
        self.questionDict2 = {"question": 'this is a question2',
                              "questionnaire": self.questionnaire,
                              }
        self.question2 = Question.objects.get_or_create(
            **self.questionDict2)[0]

        # answer
        self.answerDict = {"answer": 'this is an answer',
                           "question": self.question,
                           "correct": True
                           }
        self.answer = Answer.objects.get_or_create(**self.answerDict)[0]

        # answer2
        self.answerDict2 = {"answer": 'this is an answer2',
                            "question": self.question,
                            "correct": False
                            }
        self.answer2 = Answer.objects.get_or_create(**self.answerDict2)[0]

        # answer3
        self.answerDict3 = {"answer": 'this is an answer3',
                            "question": self.question2,
                            "correct": True
                            }
        self.answer3 = Answer.objects.get_or_create(**self.answerDict3)[0]

        # game
        self.gameDict = {
            'questionnaire': self.questionnaire,
            'publicId': 123456,
        }
        self.game = Game.objects.get_or_create(**self.gameDict)[0]

        # participant
        self.participantDict = {
            'game': self.game,
            'alias': "pepe"}
        self.participant = Participant.objects.get_or_create(**self.participantDict)[0]

        # guess
        self.guessDict={
            'participant': self.participant,
            'game': self.game,
            'question': self.question,
            'answer': self.answer,
            }
        self.guess = Guess.objects.get_or_create(**self.guessDict)[0]

    @classmethod
    def decode(cls, txt):
        return txt.decode("utf-8")

    # ==== game ====
    def test011_get_game(self):
        """Test get detail of a game given a publicID"""
        # get game information
        url = reverse(GAME_DETAIL, kwargs={'publicId': self.gameDict['publicId']} )
        response = self.client.get(path=url, format='json')
        req_body = json.loads(self.decode(response.content))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(req_body['publicId'], self.gameDict['publicId'])
       
    def test012_delete_game(self):
        # try to delete a game
        url = reverse("game-detail", kwargs={'publicId': self.gameDict['publicId']}) # get retrieve, delete, destroy, put update
        response = self.client.delete(path=url, format='json')
        # print("response", self.decode(response.content))
        games = Game.objects.filter()
        self.assertEqual(1, len(games), "It should not be possible to delete a game")
        self.assertIn(GUESS_DELETE_ERROR, self.decode(response.content) )

    def test013_update_game(self):
        # try to update a game
        url = reverse("game-detail", kwargs={'publicId': self.gameDict['publicId']}) # get retrieve, delete, destroy, put update
        data = {'publicId': 111111}
        response = self.client.put(path=url, data=data, format='json')
        games = Game.objects.filter()
        self.assertEqual(self.gameDict['publicId'], games.first().publicId, "It should not be possible to update a game")
        self.assertIn(GUESS_UPDATE_ERROR, self.decode(response.content) )

    def test014_create_game(self):
        # try to create a game
        url = reverse("game-list") # add with post, list with get
        data = {
            'questionnaire': self.questionnaire.id,
            'publicId': 222222,
        }
        response = self.client.post(path=url, data=data, format='json')
        #print("response", self.decode(response.content))
        games = Game.objects.filter()
        self.assertEqual(1, len(games), "It should not be possible to create a game")
        self.assertIn(GUESS_CREATE_ERROR, self.decode(response.content) )

    # ==== participant ====
    def test021_add_participant(self):
        url = reverse('participant-list')
        data={'game': self.gameDict['publicId'],
              'alias': "luis"}
        response = self.client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        p = Participant.objects.filter(alias='luis').first()
        self.assertEqual(data['alias'], p.alias)
        #let us add another participants with the same alias
        data={'game': self.gameDict['publicId'],
              'alias': "luis"}
        response = self.client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test022_update_participant(self):
        # try to update a participant
        url = reverse("participant-detail", kwargs={'pk': self.participant.id}) # get retrieve, delete, destroy, put update
        data = {'alias': 'Maria'}
        response = self.client.put(path=url, data=data, format='json')
        participants = Participant.objects.filter()
        self.assertEqual(self.participantDict['alias'], participants.first().alias, "It should not be possible to update a participant")
        self.assertIn(PARTICIPANT_UPDATE_ERROR, self.decode(response.content) )

    def test023_delete_participant(self):
        # try to update a participant
        url = reverse("participant-detail", kwargs={'pk': self.participant.id}) # get retrieve, delete, destroy, put update
        response = self.client.delete(path=url, format='json')
        participants = Participant.objects.filter()
        self.assertEqual(1, len(participants), "It should not be possible to delete a participant")
        self.assertIn(PARTICIPANT_DELETE_ERROR, self.decode(response.content) )

    def test024_list_participant(self):
        # try to update a participant
        url = reverse("participant-detail", kwargs={'pk': self.participant.id}) # get retrieve, delete, destroy, put update
        # print("url", url)
        response = self.client.get(path=url, format='json')
        # print("response", self.decode(response.content))
        participants = Participant.objects.filter()
        self.assertIn(PARTICIPANT_LIST_ERROR, self.decode(response.content) )

# ==== GUESS ===    
    def test_031_add_guess(self):
        url = reverse('guess-list')
        self.game.questionNo = self.game.questionNo + 1
        self.game.save()
        data={'uuidp': self.participant.uuidP,
              'game': self.gameDict['publicId'],
              #'question': self.question2.id,
              'answer': 0,
              }
        response = self.client.post(path=url, data=data, format='json')
        self.assertIn(GUESS_ERROR, self.decode(response.content))
        self.game.state = QUESTION
        self.game.save()
        response = self.client.post(path=url, data=data, format='json')
        # print("response", self.decode(response.content))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # try to answer again
        response = self.client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        guess = Guess.objects.filter().first()

    def test032_delete_guess(self):
        # try to delete a game
        url = reverse("guess-detail", kwargs={'pk': self.guess.id}) # get retrieve, delete, destroy, put update
        response = self.client.delete(path=url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # print("response", self.decode(response.content))
        guesses = Guess.objects.filter()
        self.assertEqual(1, len(guesses), "It should not be possible to delete a guess")
        self.assertIn(GUESS_DELETE_ERROR, self.decode(response.content))

    def test033_update_guess(self):
        # try to update a game
        url = reverse("guess-detail", kwargs={'pk': self.guess.id}) # get retrieve, delete, destroy, put update
        data = {'answer': 2}
        response = self.client.put(path=url, data=data, format='json')
        guesses = Guess.objects.filter()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.guess.answer.id, guesses.first().answer.id, "It should not be possible to update a guess")
        self.assertIn(GUESS_UPDATE_ERROR, self.decode(response.content) )

    def test034_detail_guess(self):
        # try to get the guess detail
        url = reverse("guess-detail", kwargs={'pk': self.guess.id}) # get retrieve, delete, destroy, put update
        response = self.client.get(path=url, format='json')
        # print("response", self.decode(response.content))
        guess = Guess.objects.filter().first()
        self.assertIn(GUESS_DELETE_ERROR, self.decode(response.content))

