from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Section, ListeningTest, Question, Option


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Rol', {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter  = ('role',)


class SectionInline(admin.TabularInline):
    model           = Section
    extra           = 4
    max_num         = 4
    fields          = ('order_num', 'audio_file', 'audio_duration_sec', 'extra_minutes')
    readonly_fields = ('audio_duration_sec',)


@admin.register(ListeningTest)
class ListeningTestAdmin(admin.ModelAdmin):
    list_display  = ('title', 'created_by', 'is_active', 'created_at')
    list_filter   = ('is_active',)   # <-- vergul qo'shildi
    search_fields = ('title',)
    inlines       = [SectionInline]  # <-- qo'shildi

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


class OptionInline(admin.TabularInline):
    model   = Option
    extra   = 4
    max_num = 4
    fields  = ('text', 'is_correct')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display  = ('section', 'order_num', 'question_type', 'text')
    list_filter   = ('question_type', 'section__test')
    search_fields = ('text',)
    inlines       = [OptionInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('section__test')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('test', 'order_num', 'audio_duration_sec', 'extra_minutes', 'get_duration_seconds')
    list_filter  = ('test',)