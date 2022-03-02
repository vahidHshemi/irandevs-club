from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, Tag
from .forms import ProjectForm, ReviewForm
from .utils import search_projects, pagination_project


# Create your views here.
def products(request):
    projects, search_query = search_projects(request)

    custom_range, projects = pagination_project(request, projects, results=6)

    context = {'projects': projects, 'search_query': search_query, 'custom_range': custom_range}
    return render(request, 'projects/multi-product.html', context=context)


def product(request, pk):
    project_obj = Project.objects.get(id=pk)
    form = ReviewForm()
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        review = form.save(commit=False)
        review.project = project_obj
        review.owner = request.user.profile
        review.save()

        project_obj.get_vote_count

        messages.success(request, 'your comment added successfully!')
        return redirect('product', pk=project_obj.id)

    # tags = product_obj.tags.all()
    return render(request, 'projects/single-product.html', {'project': project_obj, 'form': form})  # , 'tags': tags})


@login_required(login_url='login')
def create_project(request):
    profile = request.user.profile
    form = ProjectForm()

    if request.method == "POST":
        new_tags = request.POST.get('newtags').replace(",", " ").split()
        form = ProjectForm(request.POST, request.FILES)  # because client want to upload a picture for project
        if form.is_valid():  # to check form is filled correctly or not
            # form.save(commit=False)  # to store into the database
            project = form.save(commit=False)  # before storing into the database
            project.owner = profile
            project.save()
            for tag in new_tags:
                tag, created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tag)
            return redirect('account')

    context = {'form': form}
    return render(request, 'projects/project-form.html', context=context)


@login_required(login_url='login')
def update_project(request, pk):
    profile = request.user.profile
    # project = Project.objects.get(id=pk)
    project = profile.project_set.get(id=pk)  # to ensure just owner that had been logged into his account can do this
    form = ProjectForm(instance=project)

    if request.method == "POST":
        new_tags = request.POST.get('newtags').replace(",", " ").split()
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project = form.save()
            for tag in new_tags:
                tag, created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tag)
            return redirect('account')

    context = {'form': form, 'project': project}
    return render(request, 'projects/project-form.html', context=context)


@login_required(login_url='login')
def delete_project(request, pk):
    profile = request.user.profile
    # project = Project.objects.get(id=pk)
    project = profile.project_set.get(id=pk)  # to ensure just owner that had been logged into his account can do this
    if request.method == "POST":
        project.delete()
        return redirect('account')
    context = {'project': project}
    return render(request, 'projects/delete-project.html', context=context)
