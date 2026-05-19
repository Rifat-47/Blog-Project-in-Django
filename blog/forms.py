from django import forms
from django_summernote.widgets import SummernoteWidget
from .models import Post, Tag


class PostForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'cover_image', 'category', 'tags', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Post title'}),
            'content': SummernoteWidget(),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
