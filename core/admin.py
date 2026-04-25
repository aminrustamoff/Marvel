from django.contrib import admin # type: ignore
from .models import ListeningTest, ReadingTest

@admin.register(ListeningTest)
class ListeningTestAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('test_title', 'author', 'get_duration_display', 'is_active', 'created_at')
    
    # Clickable fields to enter the edit page
    list_display_links = ('test_title',)
    
    # Filter sidebar options
    list_filter = ('is_active', 'author', 'created_at')
    
    # Search bar functionality
    search_fields = ('test_title', 'test_number')
    
    # IMPORTANT: Since duration and created_at are not editable, 
    # they must be declared here to show up in the edit form.
    readonly_fields = ('duration', 'created_at')

    # Optional: Display duration in MM:SS format in the list view
    def get_duration_display(self, obj):
        if obj.duration:
            mins, secs = divmod(obj.duration, 60)
            return f"{mins}:{secs:02d}"
        return "0:00"
    get_duration_display.short_description = "Duration"

# You can also register MyModel here if needed
# admin.site.register(MyModel)

@admin.register(ReadingTest)
class ReadingTestAdmin(admin.ModelAdmin):

    list_display       = ('test_title', 'author', 'is_active', 'created_at')
    list_display_links = ('test_title',)
    list_filter        = ('is_active', 'author', 'created_at')
    list_editable      = ('is_active',)
    search_fields      = ('test_title',)
    readonly_fields    = ('created_at',)
    ordering           = ('-created_at',)

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