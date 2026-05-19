from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from blog.models import Post, ReadPost, SavedPost


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'{username}, your account has been created! You can now log in.')
            return redirect('login')
        else:
            return render(request, 'users/register.html', {'form': form})
    else:
        form = UserRegisterForm()
        return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    posts = Post.objects.filter(author=request.user).order_by('-date_posted')
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'page_obj': page_obj,
        'title': 'Profile',
        'read_count': ReadPost.objects.filter(user=request.user).count(),
        'saved_count': SavedPost.objects.filter(user=request.user).count(),
    }
    return render(request, 'users/profile.html', context)
