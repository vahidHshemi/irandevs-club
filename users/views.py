from django.shortcuts import render, redirect
from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Profile, Message
from .forms import CustomUserCreationForm, ProfileUpdate, SkillForm, MessageForm
from .utils import search_profile, paginate_profile


# Create your views here.
def loginUser(request):
    # page = 'login'

    if request.user.is_authenticated:
        return redirect('profiles')

    if request.method == "POST":
        username = request.POST['username'].lower()  # to ensure not Uppercase sensitive
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'user does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # create a user session
            return redirect(request.GET['next'] if 'next' in request.GET else 'account')
        else:
            messages.error(request, 'username or password is incorrect')

    # context = {'page': page}
    return render(request, 'users/login_register.html')


def logoutUser(request):
    logout(request)  # delete user session
    messages.info(request, 'user was logged out')
    return redirect('login')


def registerUser(request):
    page = 'register'
    # form = UserCreationForm()
    form = CustomUserCreationForm()
    if request.method == 'POST':
        # form = UserCreationForm(request.POST)
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # commit=False means that dont save current instance into th DB
            user.username = user.username.lower()
            user.save()  # now save the new user into the DB

            messages.success(request, 'user registered successfully!')
            login(request, user)
            return redirect('edit-account')
        else:
            messages.error(request, 'An error occurred during registration!')

    context = {'page': page, 'form': form}
    return render(request, 'users/login_register.html', context=context)


def profiles(request):
    profiles, search_query = search_profile(request)

    custom_range, profiles = paginate_profile(request, profiles, 6)
    context = {'profiles': profiles, 'search_query': search_query,
               'custom_range': custom_range}
    return render(request, 'users/profiles.html', context)


def user_profile(request, pk):
    userProfile = Profile.objects.get(id=pk)
    topSkills = userProfile.skill_set.exclude(description__exact="")
    otherSkills = userProfile.skill_set.filter(description="")

    context = {'userProfile': userProfile, 'topSkills': topSkills, 'otherSkills': otherSkills}
    return render(request, 'users/user-profile.html', context=context)


@login_required(login_url='login')
def user_account(request):
    profile = request.user.profile
    skills = profile.skill_set.all()
    context = {'profile': profile, 'skills': skills}
    return render(request, 'users/account.html', context=context)


@login_required(login_url='login')
def edit_account(request):
    profile = request.user.profile
    form = ProfileUpdate(instance=profile)
    if request.method == 'POST':
        form = ProfileUpdate(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('account')
    context = {'form': form}
    return render(request, 'users/profile_form.html', context=context)


@login_required(login_url='login')
def create_skill(request):
    profile = request.user.profile
    form = SkillForm()
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            skill.save()
            messages.success(request, 'skill was added successfully!')
            return redirect('account')

    context = {'form': form}
    return render(request, 'users/skill_form.html', context=context)


@login_required(login_url='login')
def update_skill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    form = SkillForm(instance=skill)
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'skill was updated successfully!')
            return redirect('account')

    context = {'form': form}
    return render(request, 'users/skill_form.html', context=context)


@login_required(login_url='login')
def delete_skill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    if request.method == 'POST':
        skill.delete()
        messages.success(request, 'skill was deleted successfully!')
        return redirect('account')

    context = {'object': skill}
    return render(request, 'users/delete_form.html', context=context)


@login_required(login_url='login')
def inbox(request):
    profile = request.user.profile
    messageRequests = profile.messages.all()
    unreadCount = messageRequests.filter(is_read=False).count()
    context = {'messageRequests': messageRequests, 'unreadCount': unreadCount}
    return render(request, 'users/inbox.html', context)


@login_required(login_url='login')
def view_message(request, pk):
    profile = request.user.profile
    message = profile.messages.get(id=pk)
    if message.is_read == False:
        message.is_read = True
        message.save()
    context = {'message': message}
    return render(request, 'users/message.html', context=context)


def create_message(request, pk):
    recipient = Profile.objects.get(id=pk)
    form = MessageForm()

    try:
        sender = request.user.profile
    except:
        sender = None

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.recipient = recipient

            if sender:
                message.name = sender.name
                message.email = sender.email

            message.save()

            messages.success(request, 'your message was successfully sent!')
            return redirect('user-profile', pk=recipient.id)
    context = {'recipient': recipient, 'form': form}
    return render(request, 'users/message_form.html', context=context)
