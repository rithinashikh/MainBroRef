from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(choices=Review.CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Review
        fields = ['comment', 'rating']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    
        
