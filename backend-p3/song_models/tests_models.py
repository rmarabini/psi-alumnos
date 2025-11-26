from django.test import TestCase
from django.contrib.auth.models import User
from .models import Song, SongUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.db import (IntegrityError, transaction,
                       connection)
# from django.urls import reverse
# from rest_framework import status

# import tempfile

from django.core.exceptions import ObjectDoesNotExist


class SongModelTest(TestCase):
    def setUp(self):
        # Crear archivos simulados
        self.audio = SimpleUploadedFile("test.mp3", b"audio content")
        self.lrc = SimpleUploadedFile("test.lrc", b"[00:00.00] Lyrics")
        self.image = SimpleUploadedFile("cover.jpg", b"image content")

    def test_00_create_song_with_valid_data(self):
        song = Song.objects.create(
            title="Test Song",
            artist="Test Artist",
            language="EN",
            category="POP",
            audio_file=self.audio,
            lrc_file=self.lrc,
            background_image=self.image
        )
        self.assertEqual(str(song), "Test Artist - Test Song")
        self.assertEqual(song.language, "EN")
        self.assertEqual(song.category, "POP")

    def test_01_invalid_language_choice(self):
        song = Song.objects.create(
            title="Invalid Language",
            artist="Test",
            language="XX",  # Not in LANGUAGE_CHOICES
            category="POP",
            audio_file=self.audio,
            lrc_file=self.lrc,
            background_image=self.image
        )
        # Para que Django valide que el valor de language está dentro de
        # LANGUAGE_CHOICES, debes llamar manualmente al método .full_clean()
        #  antes de guardar el modelo. Esto es útil especialmente en tests.
        with self.assertRaises(ValidationError):
            song.full_clean()
            song.save()

    def test_02_invalid_category_choice(self):
        song = Song.objects.create(
            title="Invalid Category",
            artist="Test",
            language="EN",
            category="POPSICOLE",  # Not in CATEGORY_CHOICES
            audio_file=self.audio,
            lrc_file=self.lrc,
            background_image=self.image
        )
        # Para que Django valide que el valor de language está dentro de
        # LANGUAGE_CHOICES, debes llamar manualmente al método .full_clean()
        #  antes de guardar el modelo. Esto es útil especialmente en tests.
        with self.assertRaises(ValidationError):
            song.full_clean()
            song.save()

    def test_10_song_play_count_increments_on_songuser_creation(self):
        """Test that the number_times_played field increments when
            a SongUser is created."""
        song = Song.objects.create(
            title="Test Song",
            artist="Test Artist",
            language="EN",
            category="POP",
            audio_file=self.audio,
            lrc_file=self.lrc,
            background_image=self.image
        )
        user = User.objects.create_user(
            username='testuser', password='testpass')
        # Initially, number_times_played should be 0
        self.assertEqual(song.number_times_played, 0)

        # Create a SongUser instance
        SongUser.objects.create(song=song, user=user)

        # Refresh the song instance from the database
        song.refresh_from_db()

        # Now, number_times_played should be 1
        self.assertEqual(song.number_times_played, 1)

        # Create another SongUser instance
        SongUser.objects.create(song=song, user=user)

        # Refresh again
        song.refresh_from_db()

        # Now, number_times_played should be 2
        self.assertEqual(song.number_times_played, 2)


class SongUserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="12345")
        self.audio = SimpleUploadedFile("test.mp3", b"audio content")
        self.lrc = SimpleUploadedFile("test.lrc", b"[00:00.00] Lyrics")
        self.image = SimpleUploadedFile("cover.jpg", b"image content")
        self.song = Song.objects.create(
            title="Test Song",
            artist="Test Artist",
            language="EN",
            category="POP",
            audio_file=self.audio,
            lrc_file=self.lrc,
            background_image=self.image
        )

    def test_10_create_song_user_relation(self):
        relation = SongUser.objects.create(
            user=self.user,
            song=self.song,
            correct_guesses=3,
            wrong_guesses=1
        )
        self.assertEqual(str(relation), "testuser - Test Song")
        self.assertEqual(relation.correct_guesses, 3)
        self.assertEqual(relation.wrong_guesses, 1)

    def test_20_song_user_with_nonexistent_song(self):
        user = User.objects.create_user(username="ghostuser", password="12345")

        # with self.assertRaises(IntegrityError):
        try:
            # Attempt to create a SongUser with a song that does not exist
            with transaction.atomic():
                SongUser.objects.create(
                    user=user,
                    song_id=9999,  # ID that does not exist
                    correct_guesses=1,
                    wrong_guesses=0
                )
                # Force commit so SQLite checks FK constraints immediately
                # not neede for postgresql
                connection.cursor().execute('COMMIT')
        except (ObjectDoesNotExist, IntegrityError) as e:
            # Handle any exception
            print(f"An error occurred: {e}")
            print(f"Exception type: {type(e).__name__}")
        else:
            self.fail("IntegrityError was not raised.")
