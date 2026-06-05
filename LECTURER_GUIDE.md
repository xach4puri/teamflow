# Lecturer Guide — Session 05: Forms & Validation

## Session Overview
**Duration:** ~80 minutes (30 min theory + 50 min live coding)
**Goal:** Students understand Django's form system, implement full CRUD for Projects and Tasks with proper validation and user feedback.
**Starting point:** Session 04 code — read-only views + templates, no ability to create/edit/delete data from the UI.

---

## What to Emphasize in This Session

### Core Concepts That MUST Land
1. **`ModelForm` is the key** — Django automatically generates form fields from model fields. You don't write `<input type="text" name="title">` manually. Show the contrast.
2. **CSRF — never skip the explanation** — Cross-Site Request Forgery is a real security attack. Explain briefly: without `{% csrf_token %}`, a malicious site could submit forms on behalf of logged-in users. Django rejects forms without it.
3. **The POST/GET pattern is universal** — Every create/edit view follows the same pattern. Learn it once, use it everywhere:
   ```
   GET → show empty/prefilled form
   POST valid → save + redirect
   POST invalid → show form with errors
   ```
4. **`form.save(commit=False)`** — Save without writing to DB. Lets you set extra fields (like `owner`) before committing. This is used every time you need to inject data the user didn't fill in.
5. **Delete confirmation pattern** — GET shows "Are you sure?", POST does the delete. Never delete on GET — it allows deletion via `<img src="/delete/1/">` cross-site attacks.

### What NOT to Over-Explain
- Don't go into `Form` vs `ModelForm` in depth — just use `ModelForm` for all cases here
- Don't show custom `clean_field()` methods yet — the validator approach is sufficient
- Don't cover formsets — they're out of scope

---

## Lecture Order (30 min)

### Block 1: Django Forms vs HTML Forms (5 min)
Show the difference:

**Manual HTML (what you'd write without Django):**
```html
<form method="post">
  <input type="text" name="title" maxlength="200" required>
  <input type="date" name="deadline">
  <!-- you'd manually validate in the view -->
</form>
```

**With Django ModelForm:**
```python
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'deadline', 'assigned_to']
```
Django generates the fields, validates types, handles errors, and re-renders with error messages. **Less code, more power.**

### Block 2: ModelForm Anatomy (8 min)
Walk through `session-05/core/forms.py`:
- `ProjectForm` — simple, just `fields = ['name', 'description']`
- `TaskForm` — more complex, with custom widgets and deadline validator
- `widgets` in `Meta` — inject CSS classes like `form-control` for Bootstrap styling
- `self.fields['deadline'].validators.append(validate_future_deadline)` — how to attach a custom validator in `__init__`

Key: **`fields` in Meta controls what the user can fill in**. `owner` is NOT in fields because it's set by the view, not the user.

### Block 3: CSRF Protection (5 min)
Show what a CSRF attack looks like (conceptually):
1. User is logged into TeamFlow
2. User visits attacker's site with: `<img src="http://teamflow.com/projects/delete/1/">`
3. Browser sends the request WITH the user's cookies — project deleted!

Django's defense: each form includes a unique hidden token. The server checks it. Other sites can't guess it.
```html
<form method="post">
  {% csrf_token %}  <!-- Django adds a hidden input with a token -->
  ...
</form>
```
**If you forget `{% csrf_token %}`, Django returns HTTP 403 Forbidden.** Students will see this.

### Block 4: Form Validation Flow (7 min)
Draw the flow:
```
POST request arrives
↓
form = ProjectForm(request.POST)
↓
form.is_valid()
├── NO → render form with errors (form.errors)
└── YES
    ↓
    form.save(commit=False)
    ↓
    project.owner = request.user  # set extra field
    ↓
    project.save()
    ↓
    redirect()
```
Show `session-05/core/validators.py` — `validate_future_deadline`:
```python
def validate_future_deadline(value):
    if value < date.today():
        raise ValidationError("Deadline cannot be in the past.")
```

### Block 5: Messages for Feedback (5 min)
Show the pattern: after every successful action, add a message and redirect:
```python
messages.success(request, f'Project "{project.name}" created!')
return redirect('core:project_detail', pk=project.pk)
```
After every failure:
```python
messages.error(request, 'Please correct the errors below.')
# re-render the form (don't redirect!)
```

---

## Live Coding Order (50 min)

> Reference files: `session-05/core/forms.py`, `session-05/core/views.py`, all form templates

### Step 1: Create forms.py (8 min)
Create `core/forms.py`:
```python
from django import forms
from .models import Project, Task
from .validators import validate_future_deadline

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
```
**Explain each part.** Then add `TaskForm` (`forms.py:36-76`).

### Step 2: Create validators.py (3 min)
Create `core/validators.py`:
```python
from django.core.exceptions import ValidationError
from datetime import date

def validate_future_deadline(value):
    if value and value < date.today():
        raise ValidationError("Deadline cannot be in the past.")
```

### Step 3: project_create view (10 min)
Type the canonical create view pattern:
```python
@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user  # set owner to logged-in user
            project.save()
            messages.success(request, f'Project "{project.name}" created!')
            return redirect('core:project_detail', pk=project.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProjectForm()
    return render(request, 'core/project_form.html', {
        'form': form, 'action': 'Create', 'title': 'Create New Project'
    })
```
**Pause at `commit=False`:** "We don't write to DB yet because we need to set `owner` first."
**Pause at `redirect` after success:** "Never re-render after POST success — use redirect to prevent double-submit."

### Step 4: project_form.html template (5 min)
Create `core/templates/core/project_form.html`:
```html
{% extends 'base.html' %}
{% block content %}
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit" class="btn btn-primary">{{ action }}</button>
</form>
{% endblock %}
```
**Demo:** Visit `/projects/create/`, submit empty form → see validation errors.

### Step 5: project_edit view (5 min)
```python
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)  # pre-fill with existing data
        if form.is_valid():
            form.save()
            ...
    else:
        form = ProjectForm(instance=project)  # pre-fill for GET
```
**Key:** `instance=project` — this tells the form which object to update. Same template as create.

### Step 6: project_delete view (5 min)
```python
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        messages.success(request, f'Project "{project.name}" deleted.')
        return redirect('core:project_list')
    return render(request, 'core/project_confirm_delete.html', {'project': project})
```
Create `project_confirm_delete.html` with:
```html
<form method="post">{% csrf_token %}
  <p>Delete "{{ project.name }}"? This will delete {{ project.tasks.count }} task(s).</p>
  <button type="submit" class="btn btn-danger">Confirm Delete</button>
  <a href="{% url 'core:project_detail' project.pk %}" class="btn btn-secondary">Cancel</a>
</form>
```

### Step 7: task_create, task_edit, task_delete (8 min)
Follow the same patterns. Show how `task_create` needs the `project_pk` from the URL:
```python
def task_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    # form.save(commit=False) then task.project = project
```

### Step 8: Update URLs (4 min)
Add all 6 new URL patterns to `core/urls.py`:
```python
path('projects/create/', views.project_create, name='project_create'),
path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
path('projects/<int:pk>/tasks/add/', views.task_create, name='task_create'),
path('tasks/<int:pk>/edit/', views.task_edit, name='task_edit'),
path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
```

### Step 9: Add Action Buttons to Templates (2 min)
Add Edit/Delete buttons to `project_detail.html` and `task_detail.html`.

---

## Full Demo Sequence
Run through the complete CRUD cycle live:
1. Create a project → see success message
2. Edit the project → see success message
3. Add a task with a past deadline → see validation error
4. Add a task with a future deadline → success
5. Delete the task → confirmation page → confirm → success message

---

## Common Student Questions

| Question | Answer |
|---|---|
| "403 Forbidden when submitting form" | You forgot `{% csrf_token %}` in the form template |
| "Form shows but saves nothing on POST" | You're not checking `request.method == 'POST'` or not calling `form.save()` |
| "How do I show individual field errors?" | `{{ form.title.errors }}` or loop `{% for field in form %}{{ field.errors }}{% endfor %}` |
| "Why `commit=False`?" | To set fields Django can't know (like `owner = request.user`) before saving |
| "What if I want to pre-select a field?" | Use `initial` parameter: `TaskForm(initial={'status': 'todo'})` |

---

## Session Checkpoint
By the end, verify each student has:
- [ ] Can create a project from the UI
- [ ] Can edit a project
- [ ] Delete shows confirmation page, then deletes
- [ ] Task create with past deadline shows error
- [ ] Success/error messages show after each action

## Homework Review (Start of Session 06)
Ask students to show their past-deadline validator. Discuss: "What happens if someone is not logged in and tries to create a project?" → Leads into auth.
