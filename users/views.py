from django.contrib import messages
from django.shortcuts import render, redirect
# from django.contrib.auth.forms import UserCreationForm
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from blog.models import Post
# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'{username}, your account has been created, now you are ready to login!')
            return redirect('login')
        else:
            return render(request, 'users/register.html', {'form':form})
    else:
        form = UserRegisterForm()
        return render(request, 'users/register.html', {'form':form})

@login_required
def profile(request):
    print(request.user)
    posts = Post.objects.filter(author=request.user).order_by('-date_posted')
    return render(request, 'users/profile.html', {'posts': posts})