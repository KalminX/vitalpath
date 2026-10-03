from django import forms
from .models import ContactMessage, WaitlistLead

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-300 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 placeholder-stone-400 text-sm',
                'placeholder': 'Your full name',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-300 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 placeholder-stone-400 text-sm',
                'placeholder': 'you@example.com',
                'required': True,
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-300 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 placeholder-stone-400 text-sm',
                'placeholder': 'Topic or course question',
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-300 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 placeholder-stone-400 text-sm',
                'placeholder': 'How can we help you?',
                'rows': 4,
                'required': True,
            }),
        }


class WaitlistForm(forms.ModelForm):
    class Meta:
        model = WaitlistLead
        fields = ['email', 'name', 'interest_area']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-300 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 placeholder-stone-400 text-sm',
                'placeholder': 'Enter your email address',
                'required': True,
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-300 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 placeholder-stone-400 text-sm',
                'placeholder': 'First name (optional)',
            }),
            'interest_area': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-stone-300 bg-white focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition text-stone-900 text-sm',
            }),
        }
