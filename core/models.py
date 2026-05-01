import os
from django.conf import settings
from django.db import models # type: ignore
from django.core.validators import MaxValueValidator # type: ignore
from mutagen.mp3 import MP3 # type: ignore
from mutagen.wave import WAVE # type: ignore
from mutagen import File # type: ignore
from django.core.exceptions import ValidationError # type: ignore

def validate_image_extension(value):
    ext = value.name.split('.')[-1].lower()
    allowed = ['jpg', 'jpeg', 'png']
    if ext not in allowed:
        raise ValidationError(f'Unsupported file type. Allowed types: {", ".join(allowed)}')
    
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

    audio_file = models.FileField(upload_to='static/listening/audios/')

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

class ListeningTestImage(models.Model):
    test = models.ForeignKey(ListeningTest, on_delete=models.CASCADE, related_name='images')
    section = models.IntegerField(choices=[(1,'Section 1'),(2,'Section 2'),(3,'Section 3'),(4,'Section 4')])
    image = models.ImageField(upload_to='static/listening/images/', validators=[validate_image_extension])
    label = models.CharField(max_length=50)  # e.g. "map", "graph", "diagram"

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

class ReadingTestImage(models.Model):
    class PassageNumber(models.IntegerChoices):
        PASSAGE_1 = 1, "Passage 1"
        PASSAGE_2 = 2, "Passage 2"
        PASSAGE_3 = 3, "Passage 3"

    test = models.ForeignKey(
        ReadingTest,
        on_delete=models.CASCADE,
        related_name='images'
    )
    passage = models.IntegerField(choices=PassageNumber.choices)
    image = models.ImageField(
        upload_to='static/reading/images/',
        validators=[validate_image_extension]
    )
    label = models.CharField(max_length=50)  # e.g. "map", "graph", "chart"

    def __str__(self):
        return f"{self.test.test_title} — Passage {self.passage} — {self.label}"
    
class WritingTask1(models.Model):
    class ReportType(models.TextChoices):
        LINE_GRAPH = 'line_graph', 'Line Graph'
        BAR_CHART = 'bar_chart', 'Bar Chart'
        PIE_CHART = 'pie_chart', 'Pie Chart'
        TABLE = 'table', 'Table'
        PROCESS = 'process', 'Process Diagram'
        MAP = 'map', 'Map'
        MIXED = 'mixed', 'Mixed Charts'

    test_title = models.CharField(max_length=250)

    question_type = models.CharField(choices=ReportType.choices)

    question = models.TextField()

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class WritingTask1Images(models.Model):
    test = models.ForeignKey(
        WritingTask1,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(
        upload_to='static/writing/images/',
        validators=[validate_image_extension]
    )
    label = models.CharField(max_length=50)  # e.g. "map", "graph", "chart"

class WritingTask2(models.Model):
    class EssayType(models.TextChoices):
        OPINION = 'opinion', 'Opinion Essay'
        DISCUSSION = 'discussion', 'Discussion Essay'
        ADVANTAGES_DISADVANTAGES = (
            'advantages_disadvantages',
            'Advantages and Disadvantages Essay'
        )
        PROBLEM_SOLUTION = 'problem_solution', 'Problem and Solution Essay'
        DIRECT_QUESTION = 'direct_question', 'Direct Question Essay'
        DOUBLE_QUESTION = 'double_question', 'Double Question Essay'

    test_title = models.CharField(max_length=250)

    question_type = models.CharField(choices=EssayType.choices)

    question = models.TextField()

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ExamSession(models.Model):
    """An exam sitting created by the admin (e.g. 'Group A – May 2026')."""
    name        = models.CharField(max_length=150)          # shown in dropdown
    description = models.CharField(max_length=300, blank=True)
    is_open     = models.BooleanField(default=True)         # admin can open/close
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"


class ResultsTable(models.Model):

    exam_session = models.ForeignKey(           # ← new
        'ExamSession',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='results'
    )
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
