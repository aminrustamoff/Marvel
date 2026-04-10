from django.db import models
from django_prose_editor.fields import ProseEditorField

class MyModel(models.Model):
    # This field will render as a Tiptap editor in the admin
    content = ProseEditorField(
        extensions={
            "Bold": True,
            "Italic": True,
            "Link": True,
            "BulletList": True,
        },
        sanitize=True  # Keeps your HTML clean and safe
    )
