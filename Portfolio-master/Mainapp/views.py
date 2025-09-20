from django.shortcuts import render, redirect, get_object_or_404
from .models import Project,Profile
from .forms import ContactForm,ProjectForm
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings




def home(request):
    projects = Project.objects.all()
    profile = Profile.objects.first()  # or filter by user if needed

  
    context = {
        'projects': projects,
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
   



def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Send email
            send_mail(
                subject=f"Portfolio Contact Form: {name}",
                message=message + f"\n\nFrom: {name} <{email}>",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            messages.success(request, "Thank you! Your message has been sent.")
            return redirect('home')
    else:
        form = ContactForm()
    return render(request, 'home', {'form': form})




def project_detail(request, id):
    project = get_object_or_404(Project, id=id)
    return render(request, 'project_detail.html', {'project': project})
