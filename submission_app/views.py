from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
import csv

from .models import InvitationToken, User, Question, Submission
from .forms import InviteRegisterForm, LoginForm, QuestionForm, SubmissionForm


# Authentication Views

def register_view(request):
    """Register a user using an invitation token."""
    token = request.GET.get('token')
    
    if not token:
        messages.error(request, 'Invalid or missing invitation token.')
        return redirect('login')
    
    try:
        invitation = InvitationToken.objects.get(token=token)
        
        if invitation.used:
            messages.error(request, 'This invitation has already been used.')
            return redirect('login')
        
        if invitation.expiry_date <= timezone.now():
            messages.error(request, 'This invitation has expired.')
            return redirect('login')
            
    except InvitationToken.DoesNotExist:
        messages.error(request, 'Invalid invitation token.')
        return redirect('login')
    
    if request.method == 'POST':
        form = InviteRegisterForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Re-fetch and lock the invitation to prevent race conditions
                invitation = InvitationToken.objects.select_for_update().get(token=token)
                
                if invitation.used:
                    messages.error(request, 'This invitation has already been used.')
                    return redirect('login')
                
                if invitation.expiry_date <= timezone.now():
                    messages.error(request, 'This invitation has expired.')
                    return redirect('login')
                
                user = User.objects.create_user(
                    username=invitation.email,
                    email=invitation.email,
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['name'],
                    role=User.Roles.APPLICANT
                )
                
                invitation.used = True
                invitation.save(update_fields=['used'])
                
                login(request, user)
                messages.success(request, 'Registration successful!')
                return redirect('applicant_dashboard')
    else:
        form = InviteRegisterForm(initial={'email': invitation.email})
    
    return render(request, 'auth/register.html', {
        'form': form,
        'email': invitation.email
    })


def login_view(request):
    """Standard login view."""
    if request.user.is_authenticated:
        if request.user.role == User.Roles.ADMIN:
            return redirect('admin_dashboard')
        return redirect('applicant_dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Authenticate using email (username field stores email)
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                
                # Redirect based on role
                user = User.objects.get(pk=user.pk)
                if user.role == User.Roles.ADMIN:
                    return redirect('admin_dashboard')
                return redirect('applicant_dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    """Logout the user."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# Applicant Views

@login_required
def applicant_dashboard(request):
    """Dashboard for applicants showing questions and progress."""
    if request.user.role != User.Roles.APPLICANT:
        return redirect('admin_dashboard')
    
    # Get all active questions
    mandatory_questions = Question.objects.filter(
        is_active=True,
        q_type=Question.QuestionType.MANDATORY
    ).order_by('difficulty')
    
    recommended_questions = Question.objects.filter(
        is_active=True,
        q_type=Question.QuestionType.RECOMMENDED
    ).order_by('difficulty')
    
    # Get user's submissions
    user_submissions = {
        sub.question.pk: sub
        for sub in Submission.objects.filter(user=request.user).select_related('question')
    }
    
    # Calculate progress
    mandatory_count = Submission.objects.filter(
        user=request.user,
        question__q_type=Question.QuestionType.MANDATORY
    ).count()
    
    total_count = Submission.objects.filter(user=request.user).count()
    
    context = {
        'mandatory_questions': mandatory_questions,
        'recommended_questions': recommended_questions,
        'user_submissions': user_submissions,
        'mandatory_count': mandatory_count,
        'total_count': total_count,
        'remaining_mandatory': max(0, 15 - mandatory_count),
        'can_finalize': mandatory_count >= 15,
        'is_finalized': request.user.is_finalized,
        'submission_form': SubmissionForm(),
    }
    
    return render(request, 'applicant/dashboard.html', context)


@login_required
@require_http_methods(["POST"])
def submit_question(request, question_id):
    """Submit a solution link for a question."""
    if request.user.role != User.Roles.APPLICANT:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    question = get_object_or_404(Question, id=question_id, is_active=True)
    form = SubmissionForm(request.POST)

    if not form.is_valid():
        messages.error(request, 'Please provide a valid submission URL.')
        return redirect('applicant_dashboard')

    submission_link = form.cleaned_data['submission_link']

    # Create or update submission with validated data
    submission, created = Submission.objects.update_or_create(
        user=request.user,
        question=question,
        defaults={'submission_link': submission_link}
    )
    
    action = 'submitted' if created else 'updated'
    messages.success(request, f'Solution {action} successfully!')
    return redirect('applicant_dashboard')


@login_required
@require_http_methods(["POST"])
def finalize_application(request):
    """Finalize the user's application."""
    if request.user.role != User.Roles.APPLICANT:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    mandatory_count = Submission.objects.filter(
        user=request.user,
        question__q_type=Question.QuestionType.MANDATORY
    ).count()
    
    if mandatory_count < 15:
        messages.error(request, f'You need to submit {15 - mandatory_count} more mandatory questions.')
        return redirect('applicant_dashboard')
    
    request.user.is_finalized = True
    request.user.save(update_fields=['is_finalized'])
    
    messages.success(request, 'Application finalized successfully!')
    return redirect('applicant_dashboard')


# Admin Views

@login_required
def admin_dashboard(request):
    """Dashboard for admin users."""
    if request.user.role != User.Roles.ADMIN:
        return redirect('applicant_dashboard')
    
    # Get statistics
    total_applicants = User.objects.filter(role=User.Roles.APPLICANT).count()
    finalized_applicants = User.objects.filter(
        role=User.Roles.APPLICANT,
        is_finalized=True
    ).count()
    total_questions = Question.objects.filter(is_active=True).count()
    total_submissions = Submission.objects.count()
    
    context = {
        'total_applicants': total_applicants,
        'finalized_applicants': finalized_applicants,
        'total_questions': total_questions,
        'total_submissions': total_submissions,
    }
    
    return render(request, 'admin/dashboard.html', context)


@login_required
def question_management(request):
    """Manage questions (CRUD operations)."""
    if request.user.role != User.Roles.ADMIN:
        return redirect('applicant_dashboard')
    
    questions = Question.objects.filter(is_active=True).order_by('q_type', 'difficulty')
    
    context = {
        'questions': questions,
    }
    
    return render(request, 'admin/questions.html', context)


@login_required
def question_create(request):
    """Create a new question."""
    if request.user.role != User.Roles.ADMIN:
        return redirect('applicant_dashboard')
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question created successfully!')
            return redirect('question_management')
    else:
        form = QuestionForm()
    
    return render(request, 'admin/question_form.html', {
        'form': form,
        'action': 'Create'
    })


@login_required
def question_edit(request, question_id):
    """Edit an existing question."""
    if request.user.role != User.Roles.ADMIN:
        return redirect('applicant_dashboard')
    
    question = get_object_or_404(Question, id=question_id)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated successfully!')
            return redirect('question_management')
    else:
        form = QuestionForm(instance=question)
    
    return render(request, 'admin/question_form.html', {
        'form': form,
        'action': 'Edit',
        'question': question
    })


@login_required
@require_http_methods(["POST"])
def question_delete(request, question_id):
    """Soft-delete a question."""
    if request.user.role != User.Roles.ADMIN:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    question = get_object_or_404(Question, id=question_id)
    question.is_active = False
    question.save(update_fields=['is_active'])
    
    messages.success(request, 'Question deactivated successfully!')
    return redirect('question_management')


@login_required
def applicant_tracker(request):
    """View and track all applicants."""
    if request.user.role != User.Roles.ADMIN:
        return redirect('applicant_dashboard')
    
    applicants = User.objects.filter(
        role=User.Roles.APPLICANT
    ).annotate(
        total_submissions=Count('submissions')
    ).order_by('-total_submissions')
    
    context = {
        'applicants': applicants,
    }
    
    return render(request, 'admin/applicants.html', context)


@login_required
def export_applicants(request):
    """Export applicants data as CSV."""
    if request.user.role != User.Roles.ADMIN:
        return redirect('applicant_dashboard')
    
    applicants = User.objects.filter(
        role=User.Roles.APPLICANT
    ).annotate(
        total_submissions=Count('submissions')
    ).order_by('-total_submissions')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="applicants.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Rank', 'Name', 'Email', 'Total Submissions', 'Finalized'])
    
    for rank, applicant in enumerate(applicants, start=1):
        writer.writerow([
            rank,
            applicant.get_full_name() or applicant.first_name or applicant.username,
            applicant.email,
            getattr(applicant, 'total_submissions', 0),
            'Yes' if applicant.is_finalized else 'No'
        ])
    
    return response
