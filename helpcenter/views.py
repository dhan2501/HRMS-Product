from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PolicyCategory, PolicyDocument
from .extraction import extract_text_from_file


def _base_template(user):
    """HR/admin users get the admin shell, everyone else (employees) get the portal shell."""
    return 'base.html' if (user.is_staff or user.is_superuser) else 'portal/base_portal.html'


# ── Help & Policies — everyone can view ────────────────────────────────────────
@login_required
def help_home(request):
    categories = PolicyCategory.objects.prefetch_related('documents').all()
    active_id  = request.GET.get('category')
    active_category = None
    if active_id:
        active_category = categories.filter(id=active_id).first()
    if not active_category:
        active_category = categories.first()

    return render(request, 'helpcenter/help_home.html', {
        'categories':       categories,
        'active_category':  active_category,
        'base_template':    _base_template(request.user),
        'is_admin':         request.user.is_staff or request.user.is_superuser,
    })


# ── Manage Policies — admin only ───────────────────────────────────────────────
@login_required
def manage_policies(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to manage policies.')
        return redirect('help_home')

    categories = PolicyCategory.objects.prefetch_related('documents').all()
    return render(request, 'helpcenter/manage_policies.html', {
        'categories': categories,
    })


@login_required
def add_category(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('help_home')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        icon = request.POST.get('icon', '').strip() or 'fa-file-lines'
        if not name:
            messages.error(request, 'Category name is required.')
        elif PolicyCategory.objects.filter(name__iexact=name).exists():
            messages.error(request, f'A category named "{name}" already exists.')
        else:
            order = PolicyCategory.objects.count()
            PolicyCategory.objects.create(name=name, icon=icon, order=order)
            messages.success(request, f'Category "{name}" created.')

    return redirect('manage_policies')


@login_required
def delete_category(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('help_home')
    cat = get_object_or_404(PolicyCategory, pk=pk)
    if request.method == 'POST':
        name = cat.name
        cat.delete()
        messages.success(request, f'Category "{name}" and its documents deleted.')
    return redirect('manage_policies')


@login_required
def add_document(request, category_id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('help_home')

    category = get_object_or_404(PolicyCategory, pk=category_id)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        notes = request.POST.get('notes', '').strip()
        uploaded_file = request.FILES.get('file')

        if not title:
            messages.error(request, 'Title is required.')
            return redirect('manage_policies')

        extracted_text, note = '', ''
        if uploaded_file:
            extracted_text, note = extract_text_from_file(uploaded_file)
            uploaded_file.seek(0)  # reset pointer so Django can still save the file

        PolicyDocument.objects.create(
            category=category,
            title=title,
            file=uploaded_file,
            extracted_text=extracted_text,
            extraction_note=note,
            notes=notes,
            uploaded_by=request.user,
        )

        if uploaded_file and not extracted_text and note:
            messages.warning(request, f'"{title}" saved, but: {note}')
        else:
            messages.success(request, f'"{title}" added to {category.name}.')

    return redirect('manage_policies')


@login_required
def delete_document(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('help_home')
    doc = get_object_or_404(PolicyDocument, pk=pk)
    if request.method == 'POST':
        title = doc.title
        doc.delete()
        messages.success(request, f'"{title}" deleted.')
    return redirect('manage_policies')