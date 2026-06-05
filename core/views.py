"""
TeamFlow Views — Session 05

Added: create, edit, delete views for Project and Task
All forms use CSRF protection ({% csrf_token %} in templates).
All create/edit/delete operations show success or error messages.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Project, Task
from .forms import ProjectForm, TaskForm
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from django.contrib.auth import login
from .forms import RegisterForm
from .models import UserProfile
from .forms import UserProfileForm


def home(request):
    context = {
        'title': 'TeamFlow',
        'tagline': 'Team Task Management Made Simple',
        'project_count': Project.objects.count(),
        'task_count': Task.objects.count(),
    }
    return render(request, 'core/home.html', context)


# ─── Project Views ─────────────────────────────────────────────────────────────

def project_list(request):
    projects = Project.objects.all().select_related('owner')
    return render(request, 'core/project_list.html', {
        'projects': projects,
        'total_count': projects.count(),
    })


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    tasks = project.tasks.all().select_related('assigned_to')
    return render(request, 'core/project_detail.html', {
        'project': project,
        'tasks': tasks,
        'task_count': tasks.count(),
        'todo_count': tasks.filter(status='todo').count(),
        'in_progress_count': tasks.filter(status='in_progress').count(),
        'done_count': tasks.filter(status='done').count(),
    })


def project_create(request):
    """
    Handles both displaying the form (GET) and submitting it (POST).

    On GET: create an empty form and render the template.
    On POST: validate the submitted data; if valid, save and redirect;
             if invalid, re-render the form with error messages.
    """
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)  # Don't save to DB yet
            project.owner = request.user       # Set the owner
            project.save()
            messages.success(request, f'Project "{project.name}" created successfully!')
            return redirect('core:project_detail', pk=project.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProjectForm()

    return render(request, 'core/project_form.html', {
        'form': form,
        'action': 'Create',
        'title': 'Create New Project',
    })


def project_edit(request, pk):
    """Edit an existing project."""
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Project "{project.name}" updated successfully!')
            return redirect('core:project_detail', pk=project.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProjectForm(instance=project)

    return render(request, 'core/project_form.html', {
        'form': form,
        'project': project,
        'action': 'Edit',
        'title': f'Edit Project: {project.name}',
    })


def project_delete(request, pk):
    """
    Shows a confirmation page on GET.
    On POST, deletes the project and redirects to the project list.
    """
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        name = project.name
        project.delete()
        messages.success(request, f'Project "{name}" deleted successfully.')
        return redirect('core:project_list')

    return render(request, 'core/project_confirm_delete.html', {
        'project': project,
    })


# ─── Task Views ────────────────────────────────────────────────────────────────

def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'core/task_detail.html', {
        'task': task,
        'project': task.project,
    })


def task_create(request, project_pk):
    """Create a new task for a specific project."""
    project = get_object_or_404(Project, pk=project_pk)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project  # Set the project
            task.save()
            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect('core:project_detail', pk=project.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaskForm()

    return render(request, 'core/task_form.html', {
        'form': form,
        'project': project,
        'action': 'Create',
        'title': f'Add Task to {project.name}',
    })


def task_edit(request, pk):
    """Edit an existing task."""
    task = get_object_or_404(Task, pk=pk)
    project = task.project
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f'Task "{task.title}" updated successfully!')
            return redirect('core:task_detail', pk=task.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaskForm(instance=task)

    return render(request, 'core/task_form.html', {
        'form': form,
        'task': task,
        'project': project,
        'action': 'Edit',
        'title': f'Edit Task: {task.title}',
    })


def task_delete(request, pk):
    """Delete confirmation + deletion for a task."""
    task = get_object_or_404(Task, pk=pk)
    project = task.project
    if request.method == 'POST':
        title = task.title
        task.delete()
        messages.success(request, f'Task "{title}" deleted successfully.')
        return redirect('core:project_detail', pk=project.pk)

    return render(request, 'core/task_confirm_delete.html', {
        'task': task,
        'project': project,
    })


def register_view(request):
    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # auto-login!
            messages.success(request,
                     f'Welcome, {user.username}!')
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Fix errors.')
    else:
        form = RegisterForm()

    return render(request, 'core/register.html', {'form': form})
    


def login_view(request):
    """User login view using Django's authenticate() function."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            # Redirect to 'next' parameter if present, otherwise to dashboard
            next_url = request.GET.get('next', '')
            if next_url:
                return redirect(next_url)
            
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'core/login.html', {})


@login_required
def project_list(request,query_param):
    """
    Shows all projects with pagination (6 per page).

    Paginator splits a queryset into pages. We get the requested
    page number from the URL query parameter: ?page=2
    """
    all_projects = Project.objects.all().select_related('owner')

    # Create a Paginator with 6 projects per page
    paginator = Paginator(all_projects, 100)
    page_number = request.GET.get('page')  # Get ?page= from URL
    page_obj = paginator.get_page(page_number)  # get_page handles invalid/missing pages

    return render(request, 'core/project_list.html'), {
        'page_obj': page_obj,
        'total_count': all_projects.count(),
    }

@login_required
def dashboard(request):
    """
    Personal dashboard showing the logged-in user's projects and assigned tasks.

    @login_required redirects unauthenticated users to the login page.
    """
    user_projects = Project.objects.filter(owner=request.user).select_related('owner')
    assigned_tasks = Task.objects.filter(assigned_to=request.user).select_related('project')

    context = {
        'user_projects': user_projects,
        'user_projects_count': user_projects.count(),
        'assigned_tasks': assigned_tasks,
        'assigned_tasks_count': assigned_tasks.count(),
        'todo_tasks': assigned_tasks.filter(status='todo').count(),
        'in_progress_tasks': assigned_tasks.filter(status='in_progress').count(),
        'done_tasks': assigned_tasks.filter(status='done').count(),
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def profile_view(request):
    profile, created = UserProfile.objects\
        .get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(
            request.POST,
            request.FILES,  # ← CRITICAL
            instance=profile
        )
        if form.is_valid():
            form.save()
            messages.success(request,
                'Profile updated!')
            return redirect('core:profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request,
        'core/profile.html',
        {'form': form, 'profile': profile})
