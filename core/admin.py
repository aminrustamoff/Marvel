from django.contrib import admin
from django.utils.html import format_html
from .models import ListeningTest, ListeningTestImage, ReadingTest, ReadingTestImage


class ListeningTestImageInline(admin.TabularInline):
    model = ListeningTestImage
    extra = 1
    fields = ('section', 'label', 'image')


class ReadingTestImageInline(admin.TabularInline):
    model = ReadingTestImage
    extra = 1
    fields = ('passage', 'label', 'image')


@admin.register(ListeningTest)
class ListeningTestAdmin(admin.ModelAdmin):
    list_display = ('test_title', 'author', 'get_duration_display', 'is_active', 'created_at')
    list_display_links = ('test_title',)
    list_filter = ('is_active', 'author', 'created_at')
    list_editable = ('is_active',)
    search_fields = ('test_title',)
    readonly_fields = ('duration', 'created_at')
    ordering = ('-created_at',)
    inlines = [ListeningTestImageInline]  # ← images managed here

    def get_duration_display(self, obj):
        if obj.duration:
            mins, secs = divmod(obj.duration, 60)
            return f"{mins}:{secs:02d}"
        return "0:00"
    get_duration_display.short_description = "Duration"


@admin.register(ReadingTest)
class ReadingTestAdmin(admin.ModelAdmin):
    list_display = ('test_title', 'author', 'is_active', 'created_at')
    list_display_links = ('test_title',)
    list_filter = ('is_active', 'author', 'created_at')
    list_editable = ('is_active',)
    search_fields = ('test_title',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    inlines = [ReadingTestImageInline]

    fieldsets = (
        ('General', {
            'fields': ('test_title', 'author', 'is_active', 'created_at'),
        }),
        ('Answer Key', {
            'fields': ('answers',),
            'classes': ('collapse',),
        }),
        ('Passage 1', {
            'fields': ('passage_1', 'passage_1_test'),
            'classes': ('collapse',),
        }),
        ('Passage 2', {
            'fields': ('passage_2', 'passage_2_test'),
            'classes': ('collapse',),
        }),
        ('Passage 3', {
            'fields': ('passage_3', 'passage_3_test'),
            'classes': ('collapse',),
        }),
    )