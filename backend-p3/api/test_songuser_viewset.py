from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from song_models.models import Song, SongUser
from django.core.files.uploadedfile import SimpleUploadedFile


class SongUserAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='pass1234')
        self.other_user = User.objects.create_user(
            username='otheruser', password='pass1234')

        dummy_audio = SimpleUploadedFile(
            "test.mp3", b"file_content", content_type="audio/mpeg")
        dummy_lrc = SimpleUploadedFile(
            "test.lrc", b"[00:00.00] Lyrics", content_type="text/plain")
        dummy_image = SimpleUploadedFile(
            "test.jpg", b"image_content", content_type="image/jpeg")

        self.song = Song.objects.create(
            title="Test Song",
            artist="Test Artist",
            language="EN",
            audio_file=dummy_audio,
            lrc_file=dummy_lrc,
            background_image=dummy_image,
            category="POP"
        )

        self.song_user = SongUser.objects.create(
            song=self.song,
            user=self.user,
            correct_guesses=3,
            wrong_guesses=1
        )

    def test_list_songusers(self):
        url = reverse('songusers-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_songuser(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('songusers-detail', args=[self.song_user.id])
        response = self.client.get(url)
        print("Response data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['song'], self.song.id)

    def test_create_songuser(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse('songusers-list')
        data = {
            "song": self.song.id,
            # "user": self.other_user.id,
            "correct_guesses": 2,
            "wrong_guesses": 0
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SongUser.objects.count(), 2)

    def test_update_songuser(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('songusers-detail', args=[self.song_user.id])
        data = {
            "song": self.song.id,
            "user": self.user.id,
            "correct_guesses": 5,
            "wrong_guesses": 2
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.song_user.refresh_from_db()
        self.assertEqual(self.song_user.correct_guesses, 5)

    def test_delete_songuser(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('songusers-detail', args=[self.song_user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(SongUser.objects.filter(id=self.song_user.id).exists())
