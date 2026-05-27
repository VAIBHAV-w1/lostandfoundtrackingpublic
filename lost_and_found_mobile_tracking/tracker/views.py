import random
import logging
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from django.utils.translation import gettext as _
from .forms import ItemReportForm, CustomUserCreationForm
from .models import ItemReport, UserProfile, Message, EmailOTP
from .utils import send_email_async

logger = logging.getLogger(__name__)

def generate_otp():
    """Generates a secure 6-digit OTP."""
    return str(random.randint(100000, 999999))

def send_otp_email(request, user, otp_type):
    """Generates, stores, and sends an OTP via email with localization support."""
    otp_code = generate_otp()
    
    # Invalidate previous unused OTPs of the same type for this user
    EmailOTP.objects.filter(user=user, otp_type=otp_type, is_used=False).update(is_used=True)
    
    # Create new OTP record
    EmailOTP.objects.create(
        user=user,
        otp_code=otp_code,
        otp_type=otp_type
    )
    
    if otp_type == EmailOTP.OTPType.SIGNUP:
        subject = _("Verify Your LostFound Account")
        message = _("Your OTP is %(code)s.\nThis code expires in 5 minutes.") % {'code': otp_code}
    elif otp_type == EmailOTP.OTPType.LOGIN:
        subject = _("Your LostFound Login Code")
        message = _("Your OTP is %(code)s.\nThis code expires in 5 minutes.") % {'code': otp_code}
    else:
        subject = _("Reset Your LostFound Password")
        message = _("Your OTP is %(code)s.\nThis code expires in 5 minutes.") % {'code': otp_code}
    
    # Use centralized async email utility
    send_email_async(subject, message, user.email)
    return True

@login_required
def home(request):
    """Home dashboard showing metrics and recent activity."""
    active_reports = ItemReport.objects.filter(status=ItemReport.StatusType.ACTIVE)
    recent = active_reports.order_by('-date_reported')[:5]
    map_data = active_reports.order_by('-date_reported')[:50]
    
    stats = {
        'total_active': active_reports.count(),
        'total_resolved': ItemReport.objects.filter(status=ItemReport.StatusType.RESOLVED).count(),
        'recent_count': recent.count(),
    }
    
    return render(request, 'tracker/home.html', {
        'recent_reports': recent,
        'map_reports': map_data,
        'stats': stats,
        'lost_count': active_reports.filter(report_type=ItemReport.ReportType.LOST).count(),
        'found_count': active_reports.filter(report_type=ItemReport.ReportType.FOUND).count(),
    })

@login_required
def report_item(request):
    """Report an item with location and details."""
    if request.method == "POST":
        form = ItemReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()
            messages.success(request, _("Successfully reported: %(title)s") % {'title': report.title})
            return redirect('tracker:profile')
    else:
        form = ItemReportForm()
    return render(request, 'tracker/report_form.html', {
        'form': form,
        'categories': ItemReport.CategoryType.choices
    })

@login_required
def search_reports(request):
    """Search for items with filtering."""
    query = request.GET.get('q', '').strip()
    r_type = request.GET.get('type', '').strip()
    category = request.GET.get('category', '').strip()
    city = request.GET.get('city', '').strip()
    
    results = ItemReport.objects.filter(status=ItemReport.StatusType.ACTIVE).order_by('-date_reported')
    
    if query:
        results = results.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if r_type:
        results = results.filter(report_type=r_type)
    if category:
        results = results.filter(category=category)
    if city:
        results = results.filter(location_name__icontains=city)
    
    return render(request, 'tracker/search.html', {
        'reports': results, 
        'query': query,
        'selected_type': r_type,
        'selected_category': category,
        'selected_city': city,
        'report_types': ItemReport.ReportType.choices,
        'categories': ItemReport.CategoryType.choices,
    })

def signup(request):
    """Signup flow with OTP verification."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        confirm_password = request.POST.get('password2')
        
        if password != confirm_password:
            messages.error(request, _("Passwords do not match."))
            return render(request, 'tracker/signup.html')
            
        if User.objects.filter(Q(username=username) | Q(email=email)).exists():
            messages.error(request, _("Username or Email already exists."))
            return render(request, 'tracker/signup.html')
            
        # Create inactive user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False
        user.save()
        UserProfile.objects.get_or_create(user=user)
        
        # Send Signup OTP
        send_otp_email(request, user, EmailOTP.OTPType.SIGNUP)
        
        # Set session data
        request.session['pending_otp_user_id'] = user.id
        request.session['otp_type'] = EmailOTP.OTPType.SIGNUP
        
        messages.success(request, _("Signup successful! Please verify the OTP sent to your email."))
        return redirect('tracker:verify_otp')
        
    return render(request, 'tracker/signup.html')

def login_view(request):
    """Login flow with 2FA OTP."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if username is actually an email
        if '@' in username:
            user_obj = User.objects.filter(email=username).first()
            if user_obj:
                username = user_obj.username

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if not user.is_active:
                # User exists but is inactive (probably didn't verify signup)
                send_otp_email(request, user, EmailOTP.OTPType.SIGNUP)
                request.session['pending_otp_user_id'] = user.id
                request.session['otp_type'] = EmailOTP.OTPType.SIGNUP
                messages.warning(request, _("Your account is not verified. A new OTP has been sent."))
                return redirect('tracker:verify_otp')
            
            # Send Login OTP (2FA)
            send_otp_email(request, user, EmailOTP.OTPType.LOGIN)
            request.session['pending_otp_user_id'] = user.id
            request.session['otp_type'] = EmailOTP.OTPType.LOGIN
            
            messages.success(request, _("Verification code sent to your email."))
            return redirect('tracker:verify_otp')
        else:
            messages.error(request, _("Invalid credentials."))
            
    return render(request, 'tracker/login.html')

def verify_otp(request):
    """Unified OTP verification view."""
    user_id = request.session.get('pending_otp_user_id')
    otp_type = request.session.get('otp_type')
    
    if not user_id or not otp_type:
        return redirect('tracker:login')
        
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        otp_record = EmailOTP.objects.filter(
            user=user, 
            otp_type=otp_type, 
            otp_code=otp_code, 
            is_used=False
        ).order_by('-created_at').first()
        
        if otp_record and otp_record.is_valid():
            otp_record.is_used = True
            otp_record.save()
            
            if otp_type == EmailOTP.OTPType.SIGNUP:
                user.is_active = True
                user.save()
                messages.success(request, _("Email verified! You can now sign in."))
                return redirect('tracker:login')
                
            elif otp_type == EmailOTP.OTPType.LOGIN:
                login(request, user)
                request.session.pop('pending_otp_user_id', None)
                request.session.pop('otp_type', None)
                return redirect('tracker:home')
                
            elif otp_type == EmailOTP.OTPType.PASSWORD_RESET:
                request.session['otp_verified_for_reset'] = True
                return render(request, 'tracker/verify_otp.html', {
                    'verified': True, 
                    'otp_type': otp_type
                })
        else:
            if otp_record:
                otp_record.attempts += 1
                otp_record.save()
            messages.error(request, _("Invalid or expired OTP."))
            
    return render(request, 'tracker/verify_otp.html', {
        'otp_type': otp_type,
        'user_email': user.email
    })

def resend_otp(request):
    """Resend OTP with cooldown protection."""
    user_id = request.session.get('pending_otp_user_id')
    otp_type = request.session.get('otp_type')
    
    if not user_id or not otp_type:
        return JsonResponse({'success': False, 'message': _('No pending session.')})
        
    user = User.objects.get(id=user_id)
    
    # Check cooldown (30 seconds)
    last_otp = EmailOTP.objects.filter(user=user, otp_type=otp_type).order_by('-created_at').first()
    if last_otp and timezone.now() < last_otp.created_at + timedelta(seconds=30):
        return JsonResponse({'success': False, 'message': _('Please wait 30 seconds before resending.')})
        
    send_otp_email(request, user, otp_type)
    return JsonResponse({'success': True, 'message': _('OTP resent successfully.')})

def forgot_password(request):
    """Forgot password flow: entry point and reset implementation."""
    if request.method == 'POST':
        if 'email' in request.POST:
            email = request.POST.get('email')
            user = User.objects.filter(email=email).first()
            if user:
                send_otp_email(request, user, EmailOTP.OTPType.PASSWORD_RESET)
                request.session['pending_otp_user_id'] = user.id
                request.session['otp_type'] = EmailOTP.OTPType.PASSWORD_RESET
                return redirect('tracker:verify_otp')
            else:
                messages.error(request, _("No account found with that email."))
                
        elif 'new_password' in request.POST:
            if not request.session.get('otp_verified_for_reset'):
                return redirect('tracker:login')
                
            new_pass = request.POST.get('new_password')
            user_id = request.session.get('pending_otp_user_id')
            user = User.objects.get(id=user_id)
            user.set_password(new_pass)
            user.save()
            
            # Clean up session
            request.session.pop('pending_otp_user_id', None)
            request.session.pop('otp_type', None)
            request.session.pop('otp_verified_for_reset', None)
            
            messages.success(request, _("Password reset successful. Please sign in."))
            return redirect('tracker:login')
            
    return render(request, 'tracker/forgot_password.html')

def logout_view(request):
    """Standard logout."""
    logout(request)
    return redirect('tracker:login')

@login_required
def user_profile(request):
    """User dashboard with reports and messages."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    my_reports = ItemReport.objects.filter(user=request.user).order_by('-date_reported')
    
    received = Message.objects.filter(recipient=request.user)
    sent = Message.objects.filter(sender=request.user)
    all_msgs = (received | sent).order_by('-timestamp')
    
    conversations = []
    seen_convs = set()
    for m in all_msgs:
        other_user = m.sender if m.recipient == request.user else m.recipient
        conv_id = (m.item.id, other_user.id)
        if conv_id not in seen_convs:
            conversations.append({
                'item': m.item,
                'other_user': other_user,
                'last_msg': m,
                'unread': not m.read and m.recipient == request.user
            })
            seen_convs.add(conv_id)

    stats = {
        'total': my_reports.count(),
        'resolved': my_reports.filter(status=ItemReport.StatusType.RESOLVED).count(),
        'messages': Message.objects.filter(recipient=request.user, read=False).count(),
    }
    
    return render(request, 'tracker/profile.html', {
        'profile': profile,
        'stats': stats,
        'my_reports': my_reports,
        'resolved_count': stats['resolved'],
        'conversations': conversations[:8],
    })

@login_required
def report_detail(request, report_id):
    """Item detail view."""
    report = get_object_or_404(ItemReport, id=report_id)
    return render(request, 'tracker/report_detail.html', {'report': report})

@login_required
def view_chat(request, report_id, other_user_id):
    """Chat thread view."""
    report = get_object_or_404(ItemReport, id=report_id)
    other_user = get_object_or_404(User, id=other_user_id)
    
    thread = Message.objects.filter(
        (Q(sender=request.user) & Q(recipient=other_user)) |
        (Q(sender=other_user) & Q(recipient=request.user)),
        item=report
    ).order_by('timestamp')
    
    thread.filter(recipient=request.user, read=False).update(read=True)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(sender=request.user, recipient=other_user, item=report, body=content)
            return redirect('tracker:chat_thread', report_id=report_id, other_user_id=other_user_id)

    return render(request, 'tracker/chat_thread.html', {
        'report': report,
        'other_user': other_user,
        'messages_list': thread
    })

@login_required
def send_message(request, report_id):
    """Initiate message contact."""
    report = get_object_or_404(ItemReport, id=report_id)
    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body and report.user and report.user != request.user:
            Message.objects.create(sender=request.user, recipient=report.user, item=report, body=body)
            messages.success(request, _("Message sent."))
            return redirect('tracker:chat_thread', report_id=report_id, other_user_id=report.user.id)
    return redirect('tracker:report_detail', report_id=report_id)

@login_required
def resolve_item(request, report_id):
    """Mark item as resolved."""
    report = get_object_or_404(ItemReport, id=report_id, user=request.user)
    report.status = ItemReport.StatusType.RESOLVED
    report.save()
    messages.success(request, _("Item marked as resolved."))
    return redirect('tracker:profile')

@login_required
def about(request):
    return render(request, 'tracker/about.html')

@login_required
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message_text = request.POST.get('message')
        
        # Send email to site owner
        subject = _("Support Message from %(name)s") % {'name': name}
        body = _("Name: %(name)s\nEmail: %(email)s\n\nMessage:\n%(message)s") % {'name': name, 'email': email, 'message': message_text}
        
        send_email_async(subject, body, 'lostandfoundtrackingpublic@gmail.com')
        
        messages.success(request, _("Message sent successfully! We will contact you soon."))
    return render(request, 'tracker/contact.html')
