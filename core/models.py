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


class ListeningSubmission(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    correct_count = models.IntegerField()
    answers = models.JSONField()
