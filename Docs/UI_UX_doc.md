# UI/UX Documentation - ScheduleBot Admin Panel

**Version:** 1.0  
**Date:** 03.12.2025  
**Target Platform:** Web (Desktop & Mobile Responsive)  
**Framework:** Bootstrap 5.3+

---

## Table of Contents

1. [Design System Overview](#design-system-overview)
2. [Color Palette](#color-palette)
3. [Typography](#typography)
4. [Component Library](#component-library)
5. [Layout Patterns](#layout-patterns)
6. [Form Guidelines](#form-guidelines)
7. [Navigation Structure](#navigation-structure)
8. [Responsive Design](#responsive-design)
9. [Accessibility](#accessibility)

---

## Design System Overview

### Philosophy
The admin panel follows a **clean, functional, data-focused design** with emphasis on:
- **Clarity:** Information is easy to read and understand
- **Efficiency:** Common actions require minimal clicks
- **Consistency:** Predictable UI patterns across all pages
- **Accessibility:** WCAG 2.1 AA compliance where possible

### Target Users
- **Primary:** AGU administrators (1-3 users)
- **Age Range:** 25-50 years old
- **Technical Skill:** Moderate (familiar with basic web forms)
- **Device:** Desktop/laptop (primary), tablet/mobile (secondary)

### Design System Foundation
- **Framework:** Bootstrap 5.3.x
- **Icons:** Bootstrap Icons or Font Awesome 6
- **Fonts:** System fonts (native, fast)
- **CSS Approach:** Utility-first with custom overrides
- **Dark Mode:** Not required for MVP

---

## Color Palette

### Primary Colors

| Color Name      | Hex Code  | Usage                          | Bootstrap Class |
|-----------------|-----------|--------------------------------|-----------------|
| Primary Blue    | `#0d6efd` | Primary actions, links         | `bg-primary`    |
| Success Green   | `#198754` | Success states, confirmations  | `bg-success`    |
| Danger Red      | `#dc3545` | Errors, delete actions         | `bg-danger`     |
| Warning Yellow  | `#ffc107` | Warnings, alerts               | `bg-warning`    |
| Info Cyan       | `#0dcaf0` | Informational messages         | `bg-info`       |

### Neutral Colors

| Color Name      | Hex Code  | Usage                          | Bootstrap Class |
|-----------------|-----------|--------------------------------|-----------------|
| Dark            | `#212529` | Primary text, headings         | `text-dark`     |
| Muted Gray      | `#6c757d` | Secondary text, labels         | `text-muted`    |
| Light Gray      | `#f8f9fa` | Backgrounds, disabled states   | `bg-light`      |
| White           | `#ffffff` | Card backgrounds, inputs       | `bg-white`      |
| Border Gray     | `#dee2e6` | Borders, dividers              | `border`        |

### Semantic Color Usage

- **Links:** Primary Blue (`#0d6efd`) - hover darker
- **Success messages:** Success Green with light background
- **Error messages:** Danger Red with light background
- **Status badges:**
  - Sent: Success Green
  - Error: Danger Red
  - Pending: Warning Yellow
  - Info: Info Cyan

---

## Typography

### Font Stack

```css
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
               "Helvetica Neue", Arial, sans-serif;
  font-size: 16px;
  line-height: 1.5;
  color: #212529;
}
```

### Type Scale

| Element          | Size  | Weight | Line Height | Bootstrap Class        |
|------------------|-------|--------|-------------|------------------------|
| Page Title (H1)  | 2rem  | 700    | 1.2         | `.display-6` or `.h1`  |
| Section (H2)     | 1.5rem| 600    | 1.3         | `.h2`                  |
| Subsection (H3)  | 1.25rem| 600   | 1.4         | `.h3`                  |
| Body Text        | 1rem  | 400    | 1.5         | Default                |
| Small Text       | 0.875rem| 400  | 1.4         | `.small`               |
| Label            | 0.875rem| 500  | 1.4         | `.form-label`          |
| Button Text      | 1rem  | 500    | 1.5         | `.btn`                 |

### Usage Guidelines

- **Page titles:** Always use H1 at top of page
- **Sections:** Use H2 for main sections (e.g., "Schedule List", "Add New Pair")
- **Form labels:** Use `<label>` with `.form-label` class
- **Help text:** Use `.form-text` or `.text-muted` for hints
- **Emphasis:** Use `<strong>` or `<em>`, not manual bolding

---

## Component Library

### 1. Buttons

#### Primary Button
```html
<button type="button" class="btn btn-primary">
  Save Changes
</button>
```
**Usage:** Main actions (Save, Submit, Send)

#### Secondary Button
```html
<button type="button" class="btn btn-secondary">
  Cancel
</button>
```
**Usage:** Secondary actions (Cancel, Back)

#### Danger Button
```html
<button type="button" class="btn btn-danger">
  Delete
</button>
```
**Usage:** Destructive actions (Delete, Remove)

#### Button with Icon
```html
<button type="button" class="btn btn-primary">
  <i class="bi bi-plus-circle"></i> Add New
</button>
```

#### Button Sizes
- Small: `.btn-sm` (use in tables)
- Default: `.btn` (use in forms)
- Large: `.btn-lg` (use for primary CTAs)

---

### 2. Cards

#### Basic Card
```html
<div class="card">
  <div class="card-header">
    <h5 class="card-title mb-0">Card Title</h5>
  </div>
  <div class="card-body">
    <p class="card-text">Card content goes here.</p>
  </div>
  <div class="card-footer text-muted">
    Optional footer
  </div>
</div>
```

**Usage:** Group related content, forms, lists

#### Dashboard Card (Stats)
```html
<div class="card text-center">
  <div class="card-body">
    <h5 class="card-title text-muted">Total Users</h5>
    <p class="display-4 mb-0">127</p>
  </div>
</div>
```

**Usage:** Display key metrics on dashboard

---

### 3. Tables

#### Standard Table
```html
<div class="table-responsive">
  <table class="table table-striped table-hover">
    <thead class="table-light">
      <tr>
        <th>#</th>
        <th>Name</th>
        <th>Course</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>1</td>
        <td>Иван Иванов</td>
        <td>2</td>
        <td>
          <button class="btn btn-sm btn-outline-primary">Edit</button>
          <button class="btn btn-sm btn-outline-danger">Delete</button>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

**Classes:**
- `.table-striped`: Zebra striping for rows
- `.table-hover`: Hover effect on rows
- `.table-sm`: Compact table
- `.table-responsive`: Horizontal scroll on small screens

**Usage:** Display lists of pairs, users, logs

---

### 4. Forms

#### Text Input
```html
<div class="mb-3">
  <label for="pairTitle" class="form-label">Pair Title</label>
  <input type="text" class="form-control" id="pairTitle" 
         placeholder="e.g., Mathematics" required>
  <div class="form-text">Enter the name of the class</div>
</div>
```

#### Select Dropdown
```html
<div class="mb-3">
  <label for="course" class="form-label">Course</label>
  <select class="form-select" id="course" required>
    <option value="">Choose...</option>
    <option value="1">1st Course</option>
    <option value="2">2nd Course</option>
    <option value="3">3rd Course</option>
    <option value="4">4th Course</option>
  </select>
</div>
```

#### Checkbox Group
```html
<div class="mb-3">
  <label class="form-label">Assign to Directions</label>
  <div class="form-check">
    <input class="form-check-input" type="checkbox" id="dir1" value="1">
    <label class="form-check-label" for="dir1">
      Direction 1 <span class="badge bg-secondary">25 users</span>
    </label>
  </div>
  <div class="form-check">
    <input class="form-check-input" type="checkbox" id="dir2" value="2">
    <label class="form-check-label" for="dir2">
      Direction 2 <span class="badge bg-secondary">30 users</span>
    </label>
  </div>
</div>
```

#### Textarea
```html
<div class="mb-3">
  <label for="message" class="form-label">Message</label>
  <textarea class="form-control" id="message" rows="5" 
            placeholder="Enter your message..."></textarea>
  <div class="form-text">Max 4096 characters (Telegram limit)</div>
</div>
```

#### Form Layout
- **Vertical:** Default (each field on new line)
- **Horizontal:** Use `.row` and `.col-*` for side-by-side fields
- **Inline:** Use `.row-cols-auto` for compact forms

---

### 5. Alerts

#### Success Alert
```html
<div class="alert alert-success alert-dismissible fade show" role="alert">
  <strong>Success!</strong> Pair created successfully.
  <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
```

#### Error Alert
```html
<div class="alert alert-danger alert-dismissible fade show" role="alert">
  <strong>Error!</strong> Failed to delete pair. Please try again.
  <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
```

**Usage:** Display feedback after actions (create, update, delete)

---

### 6. Badges

```html
<span class="badge bg-success">Sent</span>
<span class="badge bg-danger">Error</span>
<span class="badge bg-warning text-dark">Pending</span>
<span class="badge bg-secondary">25 users</span>
```

**Usage:** Display status, counts, tags

---

### 7. Modals

#### Confirmation Modal
```html
<div class="modal fade" id="deleteModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Confirm Delete</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <p>Are you sure you want to delete this pair?</p>
        <p class="text-danger mb-0">This action cannot be undone.</p>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
          Cancel
        </button>
        <button type="button" class="btn btn-danger">
          Delete
        </button>
      </div>
    </div>
  </div>
</div>
```

**Usage:** Confirmation dialogs, preview windows

---

### 8. Pagination

```html
<nav aria-label="Page navigation">
  <ul class="pagination">
    <li class="page-item disabled">
      <span class="page-link">Previous</span>
    </li>
    <li class="page-item active">
      <span class="page-link">1</span>
    </li>
    <li class="page-item">
      <a class="page-link" href="?page=2">2</a>
    </li>
    <li class="page-item">
      <a class="page-link" href="?page=3">3</a>
    </li>
    <li class="page-item">
      <a class="page-link" href="?page=2">Next</a>
    </li>
  </ul>
</nav>
```

**Usage:** Logs page, large lists (>50 items)

---

## Layout Patterns

### 1. Base Layout Structure

**File:** `base.html`

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}ScheduleBot Admin{% endblock %}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" 
        rel="stylesheet">
  <link href="/static/css/style.css" rel="stylesheet">
</head>
<body>
  <!-- Navigation -->
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container-fluid">
      <a class="navbar-brand" href="/admin">ScheduleBot Admin</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" 
              data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav">
          <li class="nav-item">
            <a class="nav-link" href="/admin">Dashboard</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/admin/pairs">Pairs</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/admin/directions">Directions</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/admin/broadcast">Broadcast</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/admin/logs">Logs</a>
          </li>
        </ul>
        <ul class="navbar-nav ms-auto">
          <li class="nav-item">
            <a class="nav-link" href="/admin/logout">Logout</a>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <!-- Main Content -->
  <main class="container my-4">
    {% block content %}{% endblock %}
  </main>

  <!-- Footer -->
  <footer class="bg-light py-3 mt-5">
    <div class="container text-center text-muted">
      <small>&copy; 2025 AGU ScheduleBot Admin Panel</small>
    </div>
  </footer>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
  <script src="/static/js/main.js"></script>
  {% block scripts %}{% endblock %}
</body>
</html>
```

---

### 2. Dashboard Layout

**Grid Structure:**
- Row 1: Stats cards (3-4 columns)
- Row 2: Recent activity table
- Row 3: Quick actions

```html
{% extends "base.html" %}

{% block content %}
<h1 class="mb-4">Dashboard</h1>

<!-- Stats Row -->
<div class="row g-3 mb-4">
  <div class="col-md-3">
    <div class="card text-center">
      <div class="card-body">
        <h6 class="text-muted">Total Users</h6>
        <p class="display-4 mb-0">{{ total_users }}</p>
      </div>
    </div>
  </div>
  <div class="col-md-3">
    <div class="card text-center">
      <div class="card-body">
        <h6 class="text-muted">Active Pairs</h6>
        <p class="display-4 mb-0">{{ total_pairs }}</p>
      </div>
    </div>
  </div>
  <div class="col-md-3">
    <div class="card text-center">
      <div class="card-body">
        <h6 class="text-muted">Messages Today</h6>
        <p class="display-4 mb-0">{{ messages_today }}</p>
      </div>
    </div>
  </div>
  <div class="col-md-3">
    <div class="card text-center">
      <div class="card-body">
        <h6 class="text-muted">Error Rate</h6>
        <p class="display-4 mb-0">{{ error_rate }}%</p>
      </div>
    </div>
  </div>
</div>

<!-- Recent Logs -->
<div class="card">
  <div class="card-header">
    <h5 class="mb-0">Recent Delivery Logs</h5>
  </div>
  <div class="card-body">
    <table class="table table-sm table-hover mb-0">
      <!-- Table content -->
    </table>
  </div>
</div>
{% endblock %}
```

---

### 3. List Page Layout (e.g., Pairs List)

```html
{% extends "base.html" %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
  <h1>Schedule Management</h1>
  <a href="/admin/pairs/new" class="btn btn-primary">
    <i class="bi bi-plus-circle"></i> Add New Pair
  </a>
</div>

<!-- Filters -->
<div class="card mb-3">
  <div class="card-body">
    <form method="get" class="row g-3">
      <div class="col-md-3">
        <label class="form-label">Course</label>
        <select name="course" class="form-select">
          <option value="">All</option>
          <option>1</option>
          <option>2</option>
        </select>
      </div>
      <div class="col-md-3">
        <label class="form-label">Day</label>
        <select name="day" class="form-select">
          <option value="">All</option>
          <option value="0">Monday</option>
          <option value="1">Tuesday</option>
        </select>
      </div>
      <div class="col-md-3 d-flex align-items-end">
        <button type="submit" class="btn btn-primary">Filter</button>
      </div>
    </form>
  </div>
</div>

<!-- Table -->
<div class="card">
  <div class="table-responsive">
    <table class="table table-hover mb-0">
      <!-- Table content -->
    </table>
  </div>
</div>
{% endblock %}
```

---

### 4. Form Page Layout (e.g., Create/Edit Pair)

```html
{% extends "base.html" %}

{% block content %}
<div class="row justify-content-center">
  <div class="col-lg-8">
    <h1 class="mb-4">{{ "Edit" if pair else "Add New" }} Pair</h1>
    
    <div class="card">
      <div class="card-body">
        <form method="post" action="/admin/pairs{{ '/' + pair.id if pair }}">
          
          <!-- Basic Info Section -->
          <h5 class="border-bottom pb-2 mb-3">Basic Information</h5>
          
          <div class="mb-3">
            <label for="title" class="form-label">Pair Title *</label>
            <input type="text" class="form-control" id="title" name="title" 
                   value="{{ pair.title if pair }}" required>
          </div>
          
          <div class="row">
            <div class="col-md-6 mb-3">
              <label for="teacher" class="form-label">Teacher (Full Name) *</label>
              <input type="text" class="form-control" id="teacher" name="teacher" 
                     value="{{ pair.teacher if pair }}" required>
            </div>
            <div class="col-md-6 mb-3">
              <label for="room" class="form-label">Room *</label>
              <input type="text" class="form-control" id="room" name="room" 
                     value="{{ pair.room if pair }}" required>
            </div>
          </div>
          
          <!-- Schedule Section -->
          <h5 class="border-bottom pb-2 mb-3 mt-4">Schedule</h5>
          
          <div class="row">
            <div class="col-md-6 mb-3">
              <label for="day_of_week" class="form-label">Day of Week *</label>
              <select class="form-select" id="day_of_week" name="day_of_week" required>
                <option value="">Choose...</option>
                <option value="0">Monday</option>
                <option value="1">Tuesday</option>
                <option value="2">Wednesday</option>
                <option value="3">Thursday</option>
                <option value="4">Friday</option>
                <option value="5">Saturday</option>
              </select>
            </div>
            <div class="col-md-6 mb-3">
              <label for="time_slot_id" class="form-label">Time Slot *</label>
              <select class="form-select" id="time_slot_id" name="time_slot_id" required>
                <option value="">Choose...</option>
                {% for slot in time_slots %}
                <option value="{{ slot.id }}">
                  {{ slot.start_time }} - {{ slot.end_time }}
                </option>
                {% endfor %}
              </select>
            </div>
          </div>
          
          <!-- Directions Section -->
          <h5 class="border-bottom pb-2 mb-3 mt-4">Assign to Directions</h5>
          <p class="text-muted">Select one or more directions</p>
          
          {% for course in [1, 2, 3, 4] %}
          <div class="mb-3">
            <h6>Course {{ course }}</h6>
            {% for direction in directions if direction.course == course %}
            <div class="form-check">
              <input class="form-check-input" type="checkbox" 
                     name="directions" value="{{ direction.id }}" 
                     id="dir{{ direction.id }}">
              <label class="form-check-label" for="dir{{ direction.id }}">
                {{ direction.name }}
                <span class="badge bg-secondary">{{ direction.user_count }} users</span>
              </label>
            </div>
            {% endfor %}
          </div>
          {% endfor %}
          
          <!-- Actions -->
          <div class="d-flex justify-content-between mt-4">
            <a href="/admin/pairs" class="btn btn-secondary">Cancel</a>
            <button type="submit" class="btn btn-primary">Save Pair</button>
          </div>
          
        </form>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

---

## Form Guidelines

### Field Requirements
1. **Required fields:** Mark with asterisk (*) in label
2. **Optional fields:** Add "(optional)" to label or leave unmarked
3. **Help text:** Use `.form-text` below input for hints
4. **Validation:** Use HTML5 validation (`required`, `min`, `max`, `pattern`)

### Error Handling
```html
<!-- Server-side error example -->
<div class="mb-3">
  <label for="title" class="form-label">Title</label>
  <input type="text" class="form-control is-invalid" id="title" value="...">
  <div class="invalid-feedback">
    Title must be at least 3 characters long.
  </div>
</div>
```

### Success States
```html
<div class="mb-3">
  <label for="email" class="form-label">Email</label>
  <input type="email" class="form-control is-valid" id="email" value="test@example.com">
  <div class="valid-feedback">
    Looks good!
  </div>
</div>
```

---

## Navigation Structure

### Primary Navigation
Located in top navbar:
1. **Dashboard** - Overview and stats
2. **Pairs** - Schedule management (CRUD)
3. **Directions** - Manage student directions
4. **Broadcast** - Send messages to users
5. **Logs** - View delivery logs

### Secondary Navigation
Breadcrumbs (optional for MVP):
```html
<nav aria-label="breadcrumb">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="/admin">Dashboard</a></li>
    <li class="breadcrumb-item"><a href="/admin/pairs">Pairs</a></li>
    <li class="breadcrumb-item active">Edit Pair</li>
  </ol>
</nav>
```

---

## Responsive Design

### Breakpoints (Bootstrap defaults)
- **xs:** <576px (mobile portrait)
- **sm:** ≥576px (mobile landscape)
- **md:** ≥768px (tablets)
- **lg:** ≥992px (laptops)
- **xl:** ≥1200px (desktops)
- **xxl:** ≥1400px (large desktops)

### Responsive Patterns

#### Dashboard Stats
- **Desktop (lg+):** 4 columns (`.col-lg-3`)
- **Tablet (md):** 2 columns (`.col-md-6`)
- **Mobile (sm):** 1 column (`.col-sm-12`)

#### Tables
- Always wrap in `.table-responsive`
- Consider card view for mobile (optional)

#### Forms
- Single column on mobile
- Two columns on desktop where appropriate

#### Navigation
- Collapsible hamburger menu on mobile
- Full menu bar on desktop

---

## Accessibility

### Best Practices
1. **Semantic HTML:** Use proper tags (`<nav>`, `<main>`, `<header>`, `<footer>`)
2. **Labels:** All inputs have associated `<label>` elements
3. **Alt text:** All images have `alt` attributes
4. **Keyboard navigation:** All interactive elements focusable
5. **ARIA labels:** Use where needed (e.g., `aria-label` for icon buttons)
6. **Color contrast:** Minimum 4.5:1 for text (Bootstrap default compliant)
7. **Focus indicators:** Visible focus states (Bootstrap default)

### Example: Accessible Button
```html
<button type="button" class="btn btn-primary" aria-label="Delete pair">
  <i class="bi bi-trash" aria-hidden="true"></i>
</button>
```

---

## Custom CSS Overrides

**File:** `static/css/style.css`

```css
/* Spacing adjustments */
.table th, .table td {
  vertical-align: middle;
}

/* Card shadows */
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

/* Sticky navbar (optional) */
.navbar {
  position: sticky;
  top: 0;
  z-index: 1020;
}

/* Badge spacing */
.badge {
  margin-left: 0.25rem;
}

/* Form section headers */
form h5 {
  color: #495057;
  font-weight: 600;
}

/* Loading spinner (optional) */
.spinner-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}
```

---

## JavaScript Interactions

**File:** `static/js/main.js`

```javascript
// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });
});

// Confirm delete actions
document.querySelectorAll('.btn-delete').forEach(btn => {
  btn.addEventListener('click', function(e) {
    if (!confirm('Are you sure you want to delete this item?')) {
      e.preventDefault();
    }
  });
});

// Character counter for textarea
const textarea = document.querySelector('textarea[maxlength]');
if (textarea) {
  const maxLength = textarea.getAttribute('maxlength');
  const counter = document.createElement('div');
  counter.className = 'form-text text-end';
  counter.textContent = `0 / ${maxLength}`;
  textarea.parentNode.appendChild(counter);
  
  textarea.addEventListener('input', function() {
    counter.textContent = `${this.value.length} / ${maxLength}`;
  });
}
```

---

## Page-Specific UI Notes

### Login Page
- Centered card (max-width: 400px)
- Simple form: password field + submit button
- No navigation bar (before authentication)
- Background: Light gradient or solid color

### Dashboard
- Focus on quick overview (stats cards)
- Recent activity table (last 10-20 logs)
- Quick action buttons (Add Pair, Send Broadcast)

### Pairs List
- Filters at top (Course, Day, Direction)
- Table with columns: Title, Teacher, Day, Slot, Directions, Actions
- Actions: Edit, Delete, Preview, Test Send
- Pagination if >50 pairs

### Pair Form
- Sectioned layout (Basic Info, Schedule, Directions)
- Direction checkboxes grouped by course
- User count badges next to directions
- Preview button (optional modal)

### Broadcast
- Large textarea for message
- Image upload (optional)
- Recipient filters (Course, Direction, All)
- Recipient count display
- Confirmation modal before send

### Logs
- Table with columns: Timestamp, User, Type, Status, Error
- Filters: Date range, Type, Status
- Pagination (20-50 per page)
- Export to CSV button (optional)

---

**Last Updated:** 03.12.2025  
**Status:** Reference for all UI implementation  
**Next:** Use components from this doc when building templates
