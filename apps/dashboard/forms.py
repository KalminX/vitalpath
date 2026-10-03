from django import forms
from django.contrib.auth.forms import AuthenticationForm
from apps.products.models import Product, ProductModule, Category
from apps.content.models import YouTubeVideo
from apps.orders.models import Customer

class CreatorLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-stone-300 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 placeholder-stone-400 text-sm',
            'placeholder': 'creator@vitalpath.edu or username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-stone-300 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 placeholder-stone-400 text-sm',
            'placeholder': '••••••••••••',
        })
    )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title', 'slug', 'category', 'price', 'currency', 'status', 'featured',
            'short_description', 'description', 'format_type', 'estimated_duration',
            'level', 'what_is_included', 'who_it_is_for', 'target_outcomes',
            'cover_image_url'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
                'placeholder': 'e.g. Health Education Fundamentals',
            }),
            'slug': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm font-mono',
                'placeholder': 'e.g. health-education-fundamentals (auto-generated if empty)',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
                'step': '0.01',
                'placeholder': '19.00',
            }),
            'currency': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm uppercase',
                'placeholder': 'USD',
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-emerald-700 rounded border-stone-300 focus:ring-emerald-700',
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
                'rows': 2,
                'placeholder': 'A concise one or two-sentence hook explaining the guide/course.',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
                'rows': 5,
                'placeholder': 'Full detailed curriculum description.',
            }),
            'format_type': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
                'placeholder': 'e.g. Digital Guide & Video Modules',
            }),
            'estimated_duration': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
                'placeholder': 'e.g. 3.5 Hours self-paced',
            }),
            'level': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
                'placeholder': 'e.g. Beginner to Intermediate',
            }),
            'what_is_included': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
                'rows': 4,
                'placeholder': 'Enter one deliverable per line\nExample:\n8 structured modules\n45-page companion PDF\nDaily action checklist',
            }),
            'who_it_is_for': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
                'rows': 3,
                'placeholder': 'Enter one target audience point per line',
            }),
            'target_outcomes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
                'rows': 3,
                'placeholder': 'Enter one key learning outcome per line',
            }),
            'cover_image_url': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
                'placeholder': 'https://images.unsplash.com/... or image path',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['category'].required = False


class YouTubeVideoForm(forms.ModelForm):
    class Meta:
        model = YouTubeVideo
        fields = ['title', 'video_id', 'description', 'thumbnail_url', 'duration', 'category', 'featured', 'is_active', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
                'placeholder': 'e.g. Understanding Macronutrients in 12 Minutes',
            }),
            'video_id': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm font-mono',
                'placeholder': 'e.g. dQw4w9WgXcQ or full YouTube URL',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
                'rows': 3,
                'placeholder': 'Summary of key principles discussed in this video lesson.',
            }),
            'thumbnail_url': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
                'placeholder': 'Leave blank to automatically use YouTube thumbnail',
            }),
            'duration': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
                'placeholder': 'e.g. 14:20',
            }),
            'category': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
                'placeholder': 'e.g. Nutrition Fundamentals',
            }),
            'order': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-emerald-700 rounded border-stone-300 focus:ring-emerald-700',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-emerald-700 rounded border-stone-300 focus:ring-emerald-700',
            }),
        }


class CustomerNotesForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
                'rows': 4,
                'placeholder': 'Internal notes about student progress, feedback, or VIP status...',
            }),
        }
