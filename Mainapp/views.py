from django.shortcuts import render, redirect, get_object_or_404
from .models import Project,Profile
from .forms import MessageForm,  ProjectForm 
from django.contrib import messages



def home(request):
    projects = Project.objects.all()
    profile = Profile.objects.first()  # or filter by user if needed

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            form.save()
            form = MessageForm()  # reset form
    else:
        form = MessageForm()

    context = {
        'projects': projects,
        'form': form,
        'profile': profile,  # ✅ pass profile to template
    }
    return render(request, 'home.html', context)



def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')  # or wherever your homepage is
    else:
        form = ProjectForm()
    return render(request, 'add_project.html', {'form': form})

def update_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'update_project.html', {'form': form, 'project': project})


def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        project.delete()
        messages.success(request, f'Project "{project.title}" deleted successfully.')
        return redirect('home')

    return render(request, 'confirm_delete.html', {'project': project})

def manage_projects(request):
    projects = Project.objects.all()
    return render(request, 'manage_projects.html', {'projects': projects})
   

