from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_project, name='add_project'),
    path('update/<int:pk>/', views.update_project, name='update_project'),
    path('delete/<int:pk>/', views.delete_project, name='delete_project'),
    path('projects/manage/', views.manage_projects, name='manage_projects'),
    path('projects/<int:id>/', views.project_detail, name='project_detail'),
     path('contact/',views.contact_view, name='contact'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)