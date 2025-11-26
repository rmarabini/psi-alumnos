from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from song_models.models import Song
from django.core.files.uploadedfile import SimpleUploadedFile


class SongAPITestCase(APITestCase):

    def setUp(self):
        # Create dummy files to use for uploads
        dummy_audio = SimpleUploadedFile(
            "test.mp3", b"file_content", content_type="audio/mpeg")
        dummy_lrc = SimpleUploadedFile(
            "test.lrc", b"[00:00.00] Lyrics", content_type="text/plain")
        dummy_image = SimpleUploadedFile(
            "test.jpg", b"image_content", content_type="image/jpeg")

        # Create multiple Song instances for testing
        # This will create 15 songs, which is more than the default page size of 10
        # to test pagination.
        for i in range(15):
            Song.objects.create(
                title=f"Test Song {i}",
                artist="Test Artist",
                language="EN",
                audio_file=dummy_audio,
                lrc_file=dummy_lrc,
                background_image=dummy_image,
                category="POP",
                number_times_played=i,
            )

    def test_01_song_list_paginated(self):
        """ Test paginated song list retrieval """
        url = reverse('songs-list')  # assuming router uses basename "song"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertLessEqual(len(response.data['results']), 10)  # page_size=10

    def test_03_song_random(self):
        """ Test random song retrieval """
        url = reverse('songs-random')  # matches @action(detail=False)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('title', response.data)
        self.assertIn('artist', response.data)

    def test_05_song_random_empty_queryset(self):
        """ Test random song retrieval when no songs are available """
        Song.objects.all().delete()
        url = reverse('songs-random')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'No songs available')

    def test_07_song_detail(self):
        """ Test retrieving an existing song detail """
        # Get an existing song ID
        song = Song.objects.first()
        url = reverse('songs-detail', args=[song.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], song.id)
        self.assertEqual(response.data['title'], song.title)

    def test_15_top_songs_default(self):
        url = reverse('songs-top')  # Adjust this name if your router uses a different basename
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertGreaterEqual(response.data[0]['number_times_played'], response.data[1]['number_times_played'])

    def test_16_top_songs_with_n_parameter(self):
        url = reverse('songs-top') + '?n=4'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_17_top_songs_invalid_n(self):
        url = reverse('songs-top') + '?n=invalid'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_20_search_song_by_title_success(self):
        url = reverse('songs-search')  # Adjust this name to match your router's name
        response = self.client.get(url, {'title': '5'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Song 5')

    def test_21_search_song_by_title_not_found(self):
        url = reverse('songs-search')
        response = self.client.get(url, {'title': 'Nonexistent'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_22_search_song_missing_query_param(self):
        url = reverse('songs-search')
        response = self.client.get(url)  # No 'title' param
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

