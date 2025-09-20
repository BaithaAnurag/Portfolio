from django.db import models



# Message Box
class Message(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



## Projects Models
class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='project_images/', blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True)

    def __str__(self):                                  
        return self.title
    
    @property
    def tags_list(self):
        return [tag.strip() for tag in self.tags.split(',')] if self.tags else []
    
    

## Profile IMage 
class Profile(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='profile_images/')

    def __str__(self):
        return self.name




# Projects Details 
class ProjectsDetails(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="details")
    descriptions = models.TextField()

    def __str__(self):
        return self.descriptions