from django.contrib import admin
from django.utils.html import format_html
from .models import Project,Profile,ProjectsDetails,ProjectView


## Project Admin
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'github_url', 'link','tags','image')


## Profile IMage 
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="120" height="120" style="border-radius: 8px;" />', obj.image.url)
        return "No image"

    image_preview.short_description = 'Profile Photo'


##Proects_Details 
@admin.register(ProjectsDetails)
class ProjectsDetailsAdmin(admin.ModelAdmin):
    list_display = ('project', 'descriptions')
    search_fields = ('descriptions',)




@admin.register(ProjectView)
class ProjectViewAdmin(admin.ModelAdmin):
    list_display = ("project", "session_id", "viewed_at")
    list_filter = ("viewed_at",)
    search_fields = ("project__title", "session_id")
