import os
from django.conf import settings
from django.db import models # type: ignore
from django.core.validators import MaxValueValidator # type: ignore
from mutagen.mp3 import MP3 # type: ignore
from mutagen.wave import WAVE # type: ignore
from mutagen import File # type: ignore

class ListeningTest(models.Model):

    test_title = models.CharField(max_length=250)

    # MORE ADVANCED, SEE IT LATER

    # class Priority(models.IntegerChoices):
    #     SECTION_1 = 1, "Section 1"
    #     SECTION_2 = 2, "Section 2"
    #     SECTION_3 = 3, "Section 3"
    #     SECTION_4 = 4, "Section 4"

    # section = models.IntegerField(
    #     choices=Priority.choices,
    #     default=Priority.SECTION_1,
    # )

    section_1 = models.TextField()
    section_2 = models.TextField()
    section_3 = models.TextField()
    section_4 = models.TextField()

    answers = models.TextField()

    audio_file = models.FileField(upload_to='audio/')

    duration = models.PositiveIntegerField(null=True, blank=True, editable=False)
    def save(self, *args, **kwargs):
        # Calculate duration if it hasn't been set yet
        if self.audio_file:
            audio = File(self.audio_file)
            if audio and audio.info:
                # Convert seconds to integer
                self.duration = int(audio.info.length)
        
        super().save(*args, **kwargs)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="posts"
    )
    
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

class ReadingTest(models.Model):
    test_title = models.CharField(max_length=250)

    passage_1 = models.TextField()
    passage_2 = models.TextField()
    passage_3 = models.TextField()
    
    passage_1_test = models.TextField()
    passage_2_test = models.TextField()
    passage_3_test = models.TextField()

    # Same format as ListeningTest.answers
    answers = models.TextField()
    
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)



class ResultsTable(models.Model):
    session_id = models.CharField(max_length=50, primary_key=True, unique=True)
    username = models.CharField(max_length=100)
    session_date = models.DateTimeField(auto_now_add=True)


class ListeningResults(models.Model):
    session = models.OneToOneField(
        'ResultsTable', 
        on_delete=models.CASCADE, 
        primary_key=True
        )
    
    test = models.ForeignKey(
        'ListeningTest', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
        )
    listening_row_answers = models.JSONField() 
    listening_correct_count = models.IntegerField()
    listening_mark = models.DecimalField(max_digits=2, decimal_places=1)

class ReadingResults(models.Model):
    session = models.OneToOneField('ResultsTable', on_delete=models.CASCADE, primary_key=True)
    test = models.ForeignKey('ReadingTest', on_delete=models.SET_NULL, null=True)
    # remove the test_id CharField — use the FK instead
    reading_row_answers = models.JSONField()
    reading_correct_count = models.IntegerField()
    reading_mark = models.DecimalField(max_digits=2, decimal_places=1)

class WritingResults(models.Model):
    session = models.OneToOneField(
        'ResultsTable', 
        on_delete=models.CASCADE, 
        primary_key=True
        )
    test_id = models.CharField(max_length=50)
    task1_text = models.TextField()
    task2_text = models.TextField()
