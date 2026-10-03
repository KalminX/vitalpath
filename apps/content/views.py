from django.shortcuts import render
from .models import YouTubeVideo, EducationalResource

def resource_hub(request):
    """
    Public resource library with educational guides and curated YouTube videos.
    """
    videos = YouTubeVideo.objects.filter(is_active=True).order_by('order', '-published_at')
    resources = EducationalResource.objects.all().order_by('order', '-published_at')

    context = {
        'videos': videos,
        'resources': resources,
    }
    return render(request, 'core/resources.html', context)
