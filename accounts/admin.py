from django.contrib import admin
from django.contrib.auth import get_user_model


@admin.register(get_user_model())
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'phone_number', 'first_name', 'last_name', 'is_verify', 'is_active', 'is_staff', 'is_superuser'
    )
    list_filter = ('is_verify', 'is_active', 'is_staff', 'is_superuser',)
    search_fields = ('id', 'phone_number', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login', 'verify_date', 'create_date')

    fieldsets = (
        ('Main', {'classes': ('collapse',), 'fields': ('phone_number', 'first_name', 'last_name',)}),
        ('Permission', {'classes': ('collapse',), 'fields': ('is_staff', 'is_active', 'is_superuser', 'is_verify')}),
        ('Date', {'classes': ('collapse',), 'fields': ('date_joined', 'last_login', 'verify_date', 'create_date')}),
    )

    add_fieldsets = fieldsets
