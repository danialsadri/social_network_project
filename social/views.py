from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (PasswordChangeView, PasswordChangeDoneView, PasswordResetView,
                                       PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView)
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from taggit.models import Tag
from .forms import *
from .models import Post, Contact, Image


def profile(request):
    try:
        user = User.objects.prefetch_related('followers', 'following').get(id=request.user.id)
    except:
        return redirect('social:login')
    saved_posts = user.saved_posts.all()[:7]
    my_posts = user.user_posts.all()[:8]
    following = user.get_followings()
    followers = user.get_followers()
    conntext = {
        'saved_posts': saved_posts,
        'my_posts': my_posts,
        'user': user,
        'following': following,
        'followers': followers,
        'form': CommentForm()
    }
    return render(request, 'social/profile.html', conntext)


def user_register(request):
    if request.user.is_authenticated:
        return redirect('social:profile')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            messages.success(request, 'با موفقیت ثبت نام کردی', 'success')
            return redirect('social:profile')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def user_edit(request):
    if request.method == 'POST':
        form = UserEditForm(data=request.POST, files=request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('social:profile')
    else:
        form = UserEditForm(instance=request.user)
    return render(request, 'registration/edit_user.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('social:profile')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, 'با موفقیت لاگین شدی', 'success')
                    return redirect('social:profile')
                else:
                    messages.error(request, 'این کاربر فعال نیست', 'danger')
                    return redirect('social:login')
            else:
                messages.error(request, 'نام کاربری یا رمز عبور اشتباه هست', 'danger')
                return redirect('social:login')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


@login_required
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('social:profile')
    return render(request, 'registration/logged_out.html')


@login_required
def ticket(request):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            message = f"{cd['name']}\n{cd['email']}\n{cd['phone']}\n\n{cd['message']}"
            send_mail(cd['subject'], message, 'danielsadri01@gmail.com', ['danielsadri01@gmail.com'], False)
            messages.success(request, 'پیام شما به پشتبانی ارسال شد', 'success')
            return redirect('social:profile')
    else:
        form = TicketForm()
    return render(request, 'forms/ticket.html', {'form': form})


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('social:password_change_done')


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'registration/password_change_done.html'


class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy('social:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('social:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'


def post_list(request, tag_slug=None):
    posts = Post.objects.select_related('author').order_by('-total_likes')
    latest_users = User.objects.filter(is_active=True).order_by('-date_joined')[:4]
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = Post.objects.filter(tags__in=[tag])
    page = request.GET.get('page')
    paginator = Paginator(posts, 2)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = []
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'social/list_ajax.html', {'posts': posts})
    context = {
        'posts': posts,
        'tag': tag,
        'latest_users': latest_users,
    }
    return render(request, "social/list.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_post = Post.objects.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_post = similar_post.annotate(same_tags=Count('tags')).order_by('-same_tags', '-created')[:4]
    context = {
        'post': post,
        'similar_post': similar_post,
        'form': CommentForm()
    }
    return render(request, "social/detail.html", context)


@login_required
def post_create(request):
    if request.method == "POST":
        form = CreatePostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            Image.objects.create(image_file=form.cleaned_data['image1'], post=post)
            Image.objects.create(image_file=form.cleaned_data['image2'], post=post)
            return redirect('social:profile')
    else:
        form = CreatePostForm()
    return render(request, 'forms/create-post.html', {'form': form})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.name = request.user.first_name
        comment.save()
    return redirect('social:profile')


def post_search(request):
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            results = Post.objects.filter(Q(description__icontains=query))
    context = {
        'results': results,
        'query': query
    }
    return render(request, 'social/search.html', context)


@login_required
@require_POST
def like_post(request):
    post_id = request.POST.get('post_id')
    if post_id is not None:
        post = get_object_or_404(Post, id=post_id)
        user = request.user
        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True
        post_likes_count = post.likes.count()
        response_data = {'liked': liked, 'likes_count': post_likes_count}
    else:
        response_data = {'error': 'Invalid post_id'}
    return JsonResponse(response_data)


@login_required
@require_POST
def save_post(request):
    post_id = request.POST.get('post_id')
    if post_id is not None:
        post = get_object_or_404(Post, id=post_id)
        user = request.user
        if user in post.saved_by.all():
            post.saved_by.remove(user)
            saved = False
        else:
            post.saved_by.add(user)
            saved = True
        response_data = {'saved': saved}
    else:
        response_data = {'error': 'Invalid request'}
    return JsonResponse(response_data)


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request, 'user/user_list.html', {'users': users})


@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    return render(request, 'user/user_detail.html', {'user': user})


@login_required
@require_POST
def user_follow(request):
    user_id = request.POST.get('id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            if request.user in user.followers.all():
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
                follow = False
            else:
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                follow = True
            following_count = user.following.count()
            followers_count = user.followers.count()
            return JsonResponse({'follow': follow, 'following_count': following_count, 'followers_count': followers_count})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User does not exist.'})
    return JsonResponse({'error': 'Invalid request.'})


def contact(request, username, rel):
    user = User.objects.get(username=username)
    if rel == 'following':
        users = user.get_followings()
    else:
        users = user.get_followers()
    return render(request, 'user/user_list.html', {'users': users})
