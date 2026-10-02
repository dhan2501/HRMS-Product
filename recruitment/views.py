from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from datetime import date
from .models import JobOpening, Candidate, Interview
from employees.models import Department, Designation


def admin_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_login')
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        try:
            from employees.models import Employee
            Employee.objects.get(user=request.user)
            return redirect('portal_dashboard')
        except:
            return redirect('employee_login')
    return wrapper


# ── Job Openings ──────────────────────────────────────────────────────────────
@admin_required
def job_list(request):
    jobs        = JobOpening.objects.select_related('department').annotate(
        candidate_count=Count('candidates')
    )
    search      = request.GET.get('search', '')
    status_f    = request.GET.get('status', '')
    dept_f      = request.GET.get('department', '')

    if search:
        jobs = jobs.filter(Q(title__icontains=search) | Q(department__name__icontains=search))
    if status_f:
        jobs = jobs.filter(status=status_f)
    if dept_f:
        jobs = jobs.filter(department_id=dept_f)

    departments = Department.objects.all()
    open_count  = JobOpening.objects.filter(status='open').count()
    total_candidates = Candidate.objects.count()

    return render(request, 'recruitment/job_list.html', {
        'jobs':             jobs,
        'departments':      departments,
        'search':           search,
        'status_f':         status_f,
        'dept_f':           dept_f,
        'open_count':       open_count,
        'total_candidates': total_candidates,
    })


@admin_required
def add_job(request):
    departments  = Department.objects.all()
    designations = Designation.objects.select_related('department').all()

    if request.method == 'POST':
        title     = request.POST.get('title', '').strip()
        dept_id   = request.POST.get('department')
        desig_id  = request.POST.get('designation') or None
        vacancies = request.POST.get('vacancies', 1)
        exp_level = request.POST.get('experience_level')
        emp_type  = request.POST.get('employment_type', 'full_time')
        desc      = request.POST.get('description', '').strip()
        reqs      = request.POST.get('requirements', '').strip()
        sal_min   = request.POST.get('salary_min') or None
        sal_max   = request.POST.get('salary_max') or None
        deadline  = request.POST.get('deadline') or None
        status    = request.POST.get('status', 'open')

        if not title or not dept_id or not exp_level or not desc:
            messages.error(request, 'Title, Department, Experience Level and Description are required.')
        else:
            job = JobOpening.objects.create(
                title=title,
                department_id=dept_id,
                designation_id=desig_id,
                vacancies=vacancies,
                experience_level=exp_level,
                employment_type=emp_type,
                description=desc,
                requirements=reqs,
                salary_min=sal_min,
                salary_max=sal_max,
                deadline=deadline,
                status=status,
            )
            messages.success(request, f'Job opening "{title}" created!')
            return redirect('job_list')

    return render(request, 'recruitment/add_job.html', {
        'departments':  departments,
        'designations': designations,
        'today':        date.today(),
    })


@admin_required
def edit_job(request, pk):
    job          = get_object_or_404(JobOpening, pk=pk)
    departments  = Department.objects.all()
    designations = Designation.objects.select_related('department').all()

    if request.method == 'POST':
        job.title            = request.POST.get('title', '').strip()
        job.department_id    = request.POST.get('department')
        job.designation_id   = request.POST.get('designation') or None
        job.vacancies        = request.POST.get('vacancies', 1)
        job.experience_level = request.POST.get('experience_level')
        job.employment_type  = request.POST.get('employment_type', 'full_time')
        job.description      = request.POST.get('description', '').strip()
        job.requirements     = request.POST.get('requirements', '').strip()
        job.salary_min       = request.POST.get('salary_min') or None
        job.salary_max       = request.POST.get('salary_max') or None
        job.deadline         = request.POST.get('deadline') or None
        job.status           = request.POST.get('status', 'open')
        job.save()
        messages.success(request, f'Job "{job.title}" updated!')
        return redirect('job_list')

    return render(request, 'recruitment/add_job.html', {
        'job':          job,
        'departments':  departments,
        'designations': designations,
        'is_edit':      True,
        'today':        date.today(),
    })


@admin_required
def delete_job(request, pk):
    job = get_object_or_404(JobOpening, pk=pk)
    if request.method == 'POST':
        title = job.title
        job.delete()
        messages.success(request, f'Job "{title}" deleted.')
    return redirect('job_list')


@admin_required
def job_detail(request, pk):
    job        = get_object_or_404(JobOpening, pk=pk)
    candidates = job.candidates.all()
    return render(request, 'recruitment/job_detail.html', {
        'job':        job,
        'candidates': candidates,
    })


# ── Candidates ────────────────────────────────────────────────────────────────
@admin_required
def candidate_list(request):
    candidates = Candidate.objects.select_related('job', 'job__department').all()
    search     = request.GET.get('search', '')
    status_f   = request.GET.get('status', '')
    job_f      = request.GET.get('job', '')

    if search:
        candidates = candidates.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)  |
            Q(email__icontains=search)
        )
    if status_f:
        candidates = candidates.filter(status=status_f)
    if job_f:
        candidates = candidates.filter(job_id=job_f)

    jobs = JobOpening.objects.filter(status='open')

    return render(request, 'recruitment/candidate_list.html', {
        'candidates': candidates,
        'jobs':       jobs,
        'search':     search,
        'status_f':   status_f,
        'job_f':      job_f,
    })


@admin_required
def add_candidate(request):
    jobs = JobOpening.objects.filter(status='open')

    if request.method == 'POST':
        job_id      = request.POST.get('job')
        first_name  = request.POST.get('first_name', '').strip()
        last_name   = request.POST.get('last_name', '').strip()
        email       = request.POST.get('email', '').strip()
        phone       = request.POST.get('phone', '').strip()
        exp         = request.POST.get('years_of_experience', 0)
        company     = request.POST.get('current_company', '').strip()
        cur_sal     = request.POST.get('current_salary') or None
        exp_sal     = request.POST.get('expected_salary') or None
        notes       = request.POST.get('notes', '').strip()
        resume      = request.FILES.get('resume')

        if not all([job_id, first_name, last_name, email, phone]):
            messages.error(request, 'Job, Name, Email and Phone are required.')
        else:
            Candidate.objects.create(
                job_id=job_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                years_of_experience=exp,
                current_company=company,
                current_salary=cur_sal,
                expected_salary=exp_sal,
                notes=notes,
                resume=resume,
                status='applied',
            )
            messages.success(request, f'{first_name} {last_name} added as candidate!')
            return redirect('candidate_list')

    return render(request, 'recruitment/add_candidate.html', {'jobs': jobs})


@admin_required
def candidate_detail(request, pk):
    candidate  = get_object_or_404(Candidate, pk=pk)
    interviews = candidate.interviews.all()
    return render(request, 'recruitment/candidate_detail.html', {
        'candidate':  candidate,
        'interviews': interviews,
    })


@admin_required
def update_candidate_status(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            candidate.status = new_status
            candidate.save()
            messages.success(request, f'Status updated to {candidate.get_status_display()}')
    return redirect('candidate_detail', pk=pk)


@admin_required
def delete_candidate(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    if request.method == 'POST':
        name = candidate.full_name
        candidate.delete()
        messages.success(request, f'Candidate "{name}" deleted.')
    return redirect('candidate_list')


# ── Interviews ────────────────────────────────────────────────────────────────
@admin_required
def interview_list(request):
    interviews = Interview.objects.select_related(
        'candidate', 'candidate__job'
    ).all()
    status_f   = request.GET.get('status', '')
    today      = date.today()

    if status_f:
        interviews = interviews.filter(status=status_f)

    upcoming   = Interview.objects.filter(
        status='scheduled',
        scheduled_at__date__gte=today
    ).count()

    return render(request, 'recruitment/interview_list.html', {
        'interviews': interviews,
        'status_f':   status_f,
        'upcoming':   upcoming,
        'today':      today,
    })


@admin_required
def schedule_interview(request, candidate_id=None):
    candidates = Candidate.objects.select_related('job').exclude(
        status__in=['hired', 'rejected', 'withdrawn']
    )
    selected_candidate = None
    if candidate_id:
        selected_candidate = get_object_or_404(Candidate, pk=candidate_id)

    if request.method == 'POST':
        cand_id     = request.POST.get('candidate')
        int_type    = request.POST.get('interview_type')
        scheduled   = request.POST.get('scheduled_at')
        duration    = request.POST.get('duration_minutes', 60)
        interviewer = request.POST.get('interviewer', '').strip()
        location    = request.POST.get('location', 'Online').strip()

        if not all([cand_id, int_type, scheduled, interviewer]):
            messages.error(request, 'Candidate, Type, Date/Time and Interviewer are required.')
        else:
            interview = Interview.objects.create(
                candidate_id=cand_id,
                interview_type=int_type,
                scheduled_at=scheduled,
                duration_minutes=duration,
                interviewer=interviewer,
                location=location,
                status='scheduled',
            )
            # Update candidate status
            candidate = get_object_or_404(Candidate, pk=cand_id)
            candidate.status = 'interview'
            candidate.save()

            messages.success(request, f'Interview scheduled for {candidate.full_name}!')
            return redirect('interview_list')

    return render(request, 'recruitment/schedule_interview.html', {
        'candidates':          candidates,
        'selected_candidate':  selected_candidate,
    })


@admin_required
def interview_detail(request, pk):
    interview = get_object_or_404(Interview, pk=pk)

    if request.method == 'POST':
        interview.status   = request.POST.get('status', interview.status)
        interview.rating   = request.POST.get('rating') or None
        interview.feedback = request.POST.get('feedback', '').strip()
        interview.save()
        messages.success(request, 'Interview updated!')
        return redirect('interview_detail', pk=pk)

    return render(request, 'recruitment/interview_detail.html', {
        'interview': interview,
    })


@admin_required
def delete_interview(request, pk):
    interview = get_object_or_404(Interview, pk=pk)
    if request.method == 'POST':
        interview.delete()
        messages.success(request, 'Interview deleted.')
    return redirect('interview_list')