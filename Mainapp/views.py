from django.shortcuts import render, redirect, get_object_or_404
from .models import Project,Profile
from .forms import ContactForm,ProjectForm
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from dotenv import load_dotenv
from .recommender import recommend_projects
from django.views.decorators.csrf import csrf_exempt
import json
from openai import OpenAI
import os

# Load .env
load_dotenv()


from django.shortcuts import render
from .models import Project, ProjectView
from .recommender import hybrid_recommend
from django.db.models import Count

def recommended_projects_page(request):
    """
    Recommended projects with Top Picks, personalized labels, tag filtering, and sorting.
    """
    last_viewed_id = request.session.get("last_viewed_project")
    projects = Project.objects.all()

    top_picks = []
    remaining_projects = []

    # Tag filter
    tag_filter = request.GET.get('tag')
    if tag_filter:
        projects = projects.filter(tags__icontains=tag_filter)

    # Sort option
    sort_option = request.GET.get('sort')
    if sort_option == 'popular':
        projects = projects.annotate(view_count=Count('projectview')).order_by('-view_count')
    elif sort_option == 'latest':
        projects = projects.order_by('-id')
    else:
        projects = projects.order_by('?')

    # Personalized hybrid recommendations
    if last_viewed_id:
        try:
            last_project = Project.objects.get(id=last_viewed_id)
            hybrid = hybrid_recommend(last_viewed_id, top_n=9)
            projects = (projects & hybrid) | hybrid
            for idx, p in enumerate(hybrid):
                p.label = f"Recommended because you viewed **{last_project.title}**"
                if idx < 2:
                    top_picks.append(p)
            remaining_projects = [p for p in projects if p not in top_picks]
        except Project.DoesNotExist:
            remaining_projects = list(projects)
    else:
        # Trending fallback
        trending = ProjectView.objects.values("project").annotate(count=Count("id")).order_by("-count")[:6]
        trending_ids = [item["project"] for item in trending]
        trending_projects = Project.objects.filter(id__in=trending_ids)
        for idx, p in enumerate(trending_projects):
            p.label = "Trending Project"
            if idx < 2:
                top_picks.append(p)
        remaining_projects = [p for p in projects if p not in top_picks]

    # Ensure every project has a label
    for p in remaining_projects:
        if not hasattr(p, "label"):
            p.label = ""

    # Unique tags
    all_tags = set()
    for p in Project.objects.all():
        if p.tags:
            for t in p.tags.split(','):
                all_tags.add(t.strip())
    all_tags = sorted(all_tags)

    context = {
        "top_picks": top_picks,
        "projects": remaining_projects,
        "all_tags": all_tags,
        "selected_tag": tag_filter,
        "selected_sort": sort_option,
    }

    return render(request, "recommended.html", context)















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
    recommendations = recommend_projects(project.id, top_n=3)
    return render(request, 'project_detail.html', {
        
        'project': project,                                            
        "recommendations": recommendations})










# Initialize OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")  # safer than hardcoding
)

@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            if not user_message:
                return JsonResponse({"error": "Message is required"}, status=400)

            # Call OpenRouter API
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",  # smaller model to save credits
                messages=[{"role": "user", "content": user_message}],
                max_tokens=200
            )

            assistant_message = response.choices[0].message.content

            return JsonResponse({"reply": assistant_message})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=405)
