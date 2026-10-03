from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from apps.products.models import Product
from apps.content.models import YouTubeVideo, EducationalResource
from .forms import ContactForm, WaitlistForm
from .models import ContactMessage, WaitlistLead
from apps.notifications.services import send_contact_notification, send_waitlist_confirmation

def home(request):
    """
    Homepage featuring value proposition, featured courses, YouTube lessons,
    learning path, and future membership preview.
    """
    featured_products = Product.objects.filter(status='published', featured=True)[:3]
    if not featured_products.exists():
        featured_products = Product.objects.filter(status='published')[:3]

    youtube_videos = YouTubeVideo.objects.filter(is_active=True, featured=True)[:4]
    if not youtube_videos.exists():
        youtube_videos = YouTubeVideo.objects.filter(is_active=True)[:4]

    waitlist_form = WaitlistForm()

    context = {
        'featured_products': featured_products,
        'youtube_videos': youtube_videos,
        'waitlist_form': waitlist_form,
    }
    return render(request, 'core/home.html', context)


def about(request):
    """
    About VitalPath Education: Philosophy, Mission, and Non-Clinical Educational Model.
    """
    return render(request, 'core/about.html')


def contact(request):
    """
    Contact page with working submission form.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_msg = form.save()
            send_contact_notification(contact_msg)
            messages.success(request, "Thank you! Your message has been received. We'll reply shortly.")
            return redirect('core:contact')
    else:
        form = ContactForm()

    return render(request, 'core/contact.html', {'form': form})


def resources(request):
    """
    Free educational resources and YouTube video library.
    """
    videos = YouTubeVideo.objects.filter(is_active=True).order_by('order', '-published_at')
    resources_list = EducationalResource.objects.all().order_by('order', '-published_at')
    waitlist_form = WaitlistForm()

    context = {
        'videos': videos,
        'resources': resources_list,
        'waitlist_form': waitlist_form,
    }
    return render(request, 'core/resources.html', context)


def waitlist_signup(request):
    """
    Waitlist signup handler for Phase 2/3 Telegram community and membership.
    """
    if request.method == 'POST':
        form = WaitlistForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            lead, created = WaitlistLead.objects.get_or_create(
                email=email,
                defaults={
                    'name': form.cleaned_data.get('name', ''),
                    'interest_area': form.cleaned_data.get('interest_area', 'all'),
                }
            )
            if created:
                send_waitlist_confirmation(lead)
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': "You're on the priority list! We will notify you first when enrollment opens."
                })
            messages.success(request, "You're on the priority list! We will notify you first when enrollment opens.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
            messages.error(request, "Please enter a valid email address.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
    return redirect('core:home')


def privacy_policy(request):
    return render(request, 'core/privacy.html')


def terms_of_service(request):
    return render(request, 'core/terms.html')


def custom_404(request, exception=None):
    return render(request, '404.html', status=404)


def custom_500(request):
    return render(request, '500.html', status=500)
