from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN   = 'admin',   'Admin'
        STUDENT = 'student', 'Student'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
    )

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def is_student(self):
        return self.role == self.Role.STUDENT

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        verbose_name        = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'


class ListeningTest(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listening_tests',
        limit_choices_to={'role': 'admin'},
    )
    title      = models.CharField(max_length=255)
    is_active  = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name        = 'Listening test'
        verbose_name_plural = 'Listening testlar'
        ordering            = ['-created_at']


class Section(models.Model):
    test      = models.ForeignKey(
        'ListeningTest',
        on_delete=models.CASCADE,
        related_name='sections',
    )
    order_num = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    audio_file         = models.FileField(upload_to='listening/audios/')
    audio_duration_sec = models.PositiveIntegerField(default=0)
    extra_minutes      = models.PositiveSmallIntegerField(default=2)

    def get_duration_seconds(self):
        return self.audio_duration_sec + (self.extra_minutes * 60)

    def save(self, *args, **kwargs):
        if self.audio_file:
            try:
                from mutagen import File as MutagenFile
                audio = MutagenFile(self.audio_file)
                if audio and audio.info:
                    self.audio_duration_sec = int(audio.info.length)
            except Exception:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.test.title} — Section {self.order_num}"

    class Meta:
        verbose_name        = 'Section'
        verbose_name_plural = 'Sectionlar'
        ordering            = ['test', 'order_num']
        unique_together     = [('test', 'order_num')]


class Question(models.Model):
    class QuestionType(models.TextChoices):
        MCQ        = 'mcq',        'Ko\'p tanlovli'
        FILL_BLANK = 'fill_blank', 'Bo\'sh joy to\'ldirish'
        TRUE_FALSE = 'true_false', 'Rost / Yolg\'on'

    section       = models.ForeignKey(
        'Section',
        on_delete=models.CASCADE,
        related_name='questions',
    )
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.MCQ,
    )
    text      = models.TextField()
    order_num = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"[{self.get_question_type_display()}] {self.text[:50]}"

    class Meta:
        verbose_name        = 'Savol'
        verbose_name_plural = 'Savollar'
        ordering            = ['section', 'order_num']
        unique_together     = [('section', 'order_num')]


class Option(models.Model):
    question   = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        related_name='options',
    )
    text       = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'to\'g\'ri' if self.is_correct else 'noto\'g\'ri'})"

    class Meta:
        verbose_name        = 'Variant'
        verbose_name_plural = 'Variantlar'