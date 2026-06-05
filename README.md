# Session 05 — Forms & Validation

## What Was Added in This Session

Building on Session 04, we added forms for creating and editing data:

1. **`core/validators.py`** — Custom form validators:
   - `validate_future_deadline` — raises `ValidationError` if deadline is in the past

2. **`core/forms.py`** — Two ModelForms:
   - `ProjectForm` — for creating/editing projects (fields: name, description)
   - `TaskForm` — for creating/editing tasks (fields: title, description, status, priority, deadline, assigned_to)
   - Bootstrap widget classes applied via `widgets` in Meta
   - Custom deadline validator attached in `TaskForm.__init__`

3. **CRUD views** for both Project and Task:
   - `project_create`, `project_edit`, `project_delete`
   - `task_create`, `task_edit`, `task_delete`
   - All views use `{% csrf_token %}` for security
   - All success/failure operations use `messages.success()` / `messages.error()`

4. **Delete confirmation pages**:
   - `project_confirm_delete.html` — shows task count warning
   - `task_confirm_delete.html` — confirms before deleting

5. **Updated URL patterns** with 8 new routes

## Key Concepts Introduced

- **ModelForms** — automatically generate forms from model fields
- **`form.is_valid()`** — triggers validation
- **`form.save(commit=False)`** — save without committing to DB (allows setting extra fields)
- **`{% csrf_token %}`** — CSRF protection, required in every POST form
- **Custom validators** — functions that raise `ValidationError`
- **`messages.success()` / `messages.error()`** — flash messages for feedback
- **Delete confirmation pattern** — GET shows confirmation, POST does the deletion

## How to Run

```bash
cd session-05
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## What to Observe

1. Create a project at **http://127.0.0.1:8000/projects/create/**
2. Try submitting with an empty name — see validation error
3. Add a task to a project, try setting a past deadline — see the custom validator error
4. Edit and delete projects and tasks — see success messages
5. Check the delete confirmation page — it warns about cascading task deletion

## What's Next

In **Session 06**, we will add user authentication (Login, Register, Logout) and protect all views with `@login_required`.
