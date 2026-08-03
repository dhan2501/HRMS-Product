# # from django.shortcuts import render, get_object_or_404, redirect
# # from django.contrib.auth.decorators import login_required
# # from django.contrib.auth.models import User
# # from django.http import JsonResponse
# # from django.views.decorators.csrf import csrf_exempt
# # from django.db.models import Q, Count
# # from django.utils import timezone
# # import json
# # from .models import Conversation, Message
# # from employees.models import Employee


# # def get_employee_or_none(user):
# #     try:
# #         return Employee.objects.select_related('department', 'designation').get(user=user)
# #     except Employee.DoesNotExist:
# #         return None


# # # ── Chat Home ─────────────────────────────────────────────────────────────────
# # @login_required
# # def chat_home(request):
# #     # Get all conversations for current user
# #     conversations = Conversation.objects.filter(
# #         participants=request.user
# #     ).prefetch_related('participants').order_by('-updated_at')

# #     # Annotate with unread count
# #     conv_data = []
# #     for conv in conversations:
# #         last_msg    = conv.last_message()
# #         unread      = conv.messages.filter(is_read=False).exclude(sender=request.user).count()
# #         other_user  = conv.get_other_participant(request.user)
# #         other_emp   = get_employee_or_none(other_user) if other_user else None

# #         conv_data.append({
# #             'conv':       conv,
# #             'last_msg':   last_msg,
# #             'unread':     unread,
# #             'other_user': other_user,
# #             'other_emp':  other_emp,
# #         })

# #     # All employees for new chat
# #     all_employees = Employee.objects.filter(
# #         status='active'
# #     ).select_related('user', 'department', 'designation').exclude(user=request.user)

# #     current_emp = get_employee_or_none(request.user)
# #     total_unread = sum(c['unread'] for c in conv_data)

# #     return render(request, 'messaging/chat_home.html', {
# #         'conv_data':     conv_data,
# #         'all_employees': all_employees,
# #         'current_emp':   current_emp,
# #         'total_unread':  total_unread,
# #     })


# # # ── Open / Start DM ───────────────────────────────────────────────────────────
# # @login_required
# # def open_chat(request, user_id):
# #     other_user = get_object_or_404(User, pk=user_id)

# #     # Find existing DM conversation
# #     conv = Conversation.objects.filter(
# #         conv_type='direct',
# #         participants=request.user
# #     ).filter(
# #         participants=other_user
# #     ).first()

# #     # Create new if not exists
# #     if not conv:
# #         conv = Conversation.objects.create(
# #             conv_type='direct',
# #             created_by=request.user
# #         )
# #         conv.participants.add(request.user, other_user)

# #     return redirect('chat_room', conv_id=conv.id)


# # # ── Chat Room ─────────────────────────────────────────────────────────────────
# # @login_required
# # # def chat_room(request, conv_id):
# # #     conv = get_object_or_404(Conversation, id=conv_id, participants=request.user)

# # #     # Mark messages as read
# # #     conv.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

# # #     messages_list = conv.messages.select_related('sender').order_by('created_at')

# # #     # All conversations for sidebar
# # #     conversations = Conversation.objects.filter(
# # #         participants=request.user
# # #     ).prefetch_related('participants').order_by('-updated_at')

# # #     conv_data = []
# # #     for c in conversations:
# # #         last_msg   = c.last_message()
# # #         unread     = c.messages.filter(is_read=False).exclude(sender=request.user).count()
# # #         other_user = c.get_other_participant(request.user)
# # #         other_emp  = get_employee_or_none(other_user) if other_user else None
# # #         conv_data.append({
# # #             'conv': c, 'last_msg': last_msg,
# # #             'unread': unread, 'other_user': other_user, 'other_emp': other_emp,
# # #             'is_active': c.id == conv.id,
# # #         })

# # #     other_user = conv.get_other_participant(request.user)
# # #     other_emp  = get_employee_or_none(other_user) if other_user else None
# # #     current_emp = get_employee_or_none(request.user)
# # #     all_employees = Employee.objects.filter(
# # #         status='active'
# # #     ).select_related('user', 'department').exclude(user=request.user)

# # #     return render(request, 'messaging/chat_room.html', {
# # #         'conv':          conv,
# # #         'messages_list': messages_list,
# # #         'conv_data':     conv_data,
# # #         'other_user':    other_user,
# # #         'other_emp':     other_emp,
# # #         'current_emp':   current_emp,
# # #         'all_employees': all_employees,
# # #     })

# # def chat_room(request, conv_id):
# #     conv = get_object_or_404(Conversation, id=conv_id, participants=request.user)

# #     # Mark messages as read
# #     conv.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

# #     messages_list = conv.messages.select_related('sender').order_by('created_at')

# #     # All conversations for sidebar
# #     conversations = Conversation.objects.filter(
# #         participants=request.user
# #     ).prefetch_related('participants').order_by('-updated_at')

# #     conv_data = []
# #     for c in conversations:
# #         last_msg   = c.last_message()
# #         unread     = c.messages.filter(is_read=False).exclude(sender=request.user).count()
# #         other_user = c.get_other_participant(request.user)
# #         other_emp  = get_employee_or_none(other_user) if other_user else None
# #         conv_data.append({
# #             'conv': c, 'last_msg': last_msg,
# #             'unread': unread, 'other_user': other_user, 'other_emp': other_emp,
# #             'is_active': c.id == conv.id,
# #         })

# #     other_user = conv.get_other_participant(request.user)
# #     other_emp  = get_employee_or_none(other_user) if other_user else None
# #     current_emp = get_employee_or_none(request.user)
# #     all_employees = Employee.objects.filter(
# #         status='active'
# #     ).select_related('user', 'department').exclude(user=request.user)

# #     return render(request, 'messaging/chat_home.html', {
# #         'conv':          conv,
# #         'messages_list': messages_list,
# #         'conv_data':     conv_data,
# #         'other_user':    other_user,
# #         'other_emp':     other_emp,
# #         'current_emp':   current_emp,
# #         'all_employees': all_employees,
# #     })


# # # ── Send Message (AJAX) ───────────────────────────────────────────────────────
# # @login_required
# # def send_message(request, conv_id):
# #     if request.method != 'POST':
# #         return JsonResponse({'error': 'POST only'}, status=405)

# #     conv = get_object_or_404(Conversation, id=conv_id, participants=request.user)
# #     content = request.POST.get('content', '').strip()

# #     if not content:
# #         return JsonResponse({'error': 'Empty message'}, status=400)

# #     msg = Message.objects.create(
# #         conversation=conv,
# #         sender=request.user,
# #         content=content,
# #     )

# #     # Update conversation timestamp
# #     conv.updated_at = timezone.now()
# #     conv.save(update_fields=['updated_at'])

# #     emp = get_employee_or_none(request.user)
# #     initials = ''
# #     if emp:
# #         initials = f"{emp.first_name[0]}{emp.last_name[0]}".upper()
# #     else:
# #         initials = request.user.username[:2].upper()

# #     return JsonResponse({
# #         'id':         msg.id,
# #         'content':    msg.content,
# #         'sender':     request.user.get_full_name() or request.user.username,
# #         'initials':   initials,
# #         'photo':      emp.photo.url if emp and emp.photo else None,
# #         'time':       msg.created_at.strftime('%I:%M %p'),
# #         'is_mine':    True,
# #     })


# # # ── Poll New Messages (AJAX) ──────────────────────────────────────────────────
# # @login_required
# # def poll_messages(request, conv_id):
# #     conv        = get_object_or_404(Conversation, id=conv_id, participants=request.user)
# #     last_id     = int(request.GET.get('last_id', 0))
# #     new_msgs    = conv.messages.filter(id__gt=last_id).select_related('sender').order_by('created_at')

# #     # Mark as read
# #     new_msgs.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

# #     msgs_data = []
# #     for msg in new_msgs:
# #         emp      = get_employee_or_none(msg.sender)
# #         initials = ''
# #         if emp:
# #             initials = f"{emp.first_name[0]}{emp.last_name[0]}".upper()
# #         else:
# #             initials = msg.sender.username[:2].upper()

# #         msgs_data.append({
# #             'id':       msg.id,
# #             'content':  msg.content,
# #             'sender':   msg.sender.get_full_name() or msg.sender.username,
# #             'initials': initials,
# #             'photo':    emp.photo.url if emp and emp.photo else None,
# #             'time':     msg.created_at.strftime('%I:%M %p'),
# #             'is_mine':  msg.sender == request.user,
# #         })

# #     return JsonResponse({'messages': msgs_data})


# # # ── Unread Count (AJAX) ───────────────────────────────────────────────────────
# # @login_required
# # def unread_count(request):
# #     count = Message.objects.filter(
# #         conversation__participants=request.user,
# #         is_read=False
# #     ).exclude(sender=request.user).count()
# #     return JsonResponse({'count': count})


# # # ── Create Group Chat ─────────────────────────────────────────────────────────
# # @login_required
# # def create_group(request):
# #     if request.method == 'POST':
# #         name        = request.POST.get('name', '').strip()
# #         member_ids  = request.POST.getlist('members')

# #         if not name:
# #             from django.contrib import messages
# #             messages.error(request, 'Group name is required.')
# #             return redirect('chat_home')

# #         conv = Conversation.objects.create(
# #             conv_type='group',
# #             name=name,
# #             created_by=request.user,
# #         )
# #         conv.participants.add(request.user)
# #         for uid in member_ids:
# #             try:
# #                 user = User.objects.get(pk=uid)
# #                 conv.participants.add(user)
# #             except User.DoesNotExist:
# #                 pass

# #         # Welcome message
# #         Message.objects.create(
# #             conversation=conv,
# #             sender=request.user,
# #             content=f"🎉 Group '{name}' created! Welcome everyone.",
# #         )

# #         return redirect('chat_room', conv_id=conv.id)

# #     return redirect('chat_home')



# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.db.models import Q, Count
# from django.utils import timezone
# import json
# from .models import Conversation, Message
# from employees.models import Employee


# def get_employee_or_none(user):
#     try:
#         return Employee.objects.select_related('department', 'designation').get(user=user)
#     except Employee.DoesNotExist:
#         return None


# def _base_template(user):
#     """HR/admin users get the admin shell, everyone else (employees) get the portal shell."""
#     return 'base.html' if (user.is_staff or user.is_superuser) else 'portal/base_portal.html'


# # ── Chat Home ─────────────────────────────────────────────────────────────────
# @login_required
# def chat_home(request):
#     # Get all conversations for current user
#     conversations = Conversation.objects.filter(
#         participants=request.user
#     ).prefetch_related('participants').order_by('-updated_at')

#     # Annotate with unread count
#     conv_data = []
#     for conv in conversations:
#         last_msg    = conv.last_message()
#         unread      = conv.messages.filter(is_read=False).exclude(sender=request.user).count()
#         other_user  = conv.get_other_participant(request.user)
#         other_emp   = get_employee_or_none(other_user) if other_user else None

#         conv_data.append({
#             'conv':       conv,
#             'last_msg':   last_msg,
#             'unread':     unread,
#             'other_user': other_user,
#             'other_emp':  other_emp,
#         })

#     # All employees for new chat — every active employee, HR or not,
#     # so any individual can start a 1:1 chat with any colleague.
#     all_employees = Employee.objects.filter(
#         status='active'
#     ).select_related('user', 'department', 'designation').exclude(user=request.user)

#     current_emp = get_employee_or_none(request.user)
#     total_unread = sum(c['unread'] for c in conv_data)

#     return render(request, 'messaging/chat_home.html', {
#         'conv_data':     conv_data,
#         'all_employees': all_employees,
#         'current_emp':   current_emp,
#         'total_unread':  total_unread,
#         'base_template': _base_template(request.user),
#     })


# # ── Open / Start DM ───────────────────────────────────────────────────────────
# @login_required
# def open_chat(request, user_id):
#     other_user = get_object_or_404(User, pk=user_id)

#     # Find existing DM conversation
#     conv = Conversation.objects.filter(
#         conv_type='direct',
#         participants=request.user
#     ).filter(
#         participants=other_user
#     ).first()

#     # Create new if not exists
#     if not conv:
#         conv = Conversation.objects.create(
#             conv_type='direct',
#             created_by=request.user
#         )
#         conv.participants.add(request.user, other_user)

#     return redirect('chat_room', conv_id=conv.id)


# # ── Chat Room ─────────────────────────────────────────────────────────────────
# @login_required
# def chat_room(request, conv_id):
#     conv = get_object_or_404(Conversation, id=conv_id, participants=request.user)

#     # Mark messages as read
#     conv.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

#     messages_list = conv.messages.select_related('sender').order_by('created_at')

#     # All conversations for sidebar
#     conversations = Conversation.objects.filter(
#         participants=request.user
#     ).prefetch_related('participants').order_by('-updated_at')

#     conv_data = []
#     for c in conversations:
#         last_msg   = c.last_message()
#         unread     = c.messages.filter(is_read=False).exclude(sender=request.user).count()
#         other_user = c.get_other_participant(request.user)
#         other_emp  = get_employee_or_none(other_user) if other_user else None
#         conv_data.append({
#             'conv': c, 'last_msg': last_msg,
#             'unread': unread, 'other_user': other_user, 'other_emp': other_emp,
#             'is_active': c.id == conv.id,
#         })

#     other_user = conv.get_other_participant(request.user)
#     other_emp  = get_employee_or_none(other_user) if other_user else None
#     current_emp = get_employee_or_none(request.user)
#     all_employees = Employee.objects.filter(
#         status='active'
#     ).select_related('user', 'department').exclude(user=request.user)

#     return render(request, 'messaging/chat_home.html', {
#         'conv':          conv,
#         'messages_list': messages_list,
#         'conv_data':     conv_data,
#         'other_user':    other_user,
#         'other_emp':     other_emp,
#         'current_emp':   current_emp,
#         'all_employees': all_employees,
#         'base_template': _base_template(request.user),
#     })


# # ── Send Message (AJAX) ───────────────────────────────────────────────────────
# @login_required
# def send_message(request, conv_id):
#     if request.method != 'POST':
#         return JsonResponse({'error': 'POST only'}, status=405)

#     conv = get_object_or_404(Conversation, id=conv_id, participants=request.user)
#     content = request.POST.get('content', '').strip()

#     if not content:
#         return JsonResponse({'error': 'Empty message'}, status=400)

#     msg = Message.objects.create(
#         conversation=conv,
#         sender=request.user,
#         content=content,
#     )

#     # Update conversation timestamp
#     conv.updated_at = timezone.now()
#     conv.save(update_fields=['updated_at'])

#     emp = get_employee_or_none(request.user)
#     initials = ''
#     if emp:
#         initials = f"{emp.first_name[0]}{emp.last_name[0]}".upper()
#     else:
#         initials = request.user.username[:2].upper()

#     return JsonResponse({
#         'id':         msg.id,
#         'content':    msg.content,
#         'sender':     request.user.get_full_name() or request.user.username,
#         'initials':   initials,
#         'photo':      emp.photo.url if emp and emp.photo else None,
#         'time':       msg.created_at.strftime('%I:%M %p'),
#         'is_mine':    True,
#     })


# # ── Poll New Messages (AJAX) ──────────────────────────────────────────────────
# @login_required
# def poll_messages(request, conv_id):
#     conv        = get_object_or_404(Conversation, id=conv_id, participants=request.user)
#     last_id     = int(request.GET.get('last_id', 0))
#     new_msgs    = conv.messages.filter(id__gt=last_id).select_related('sender').order_by('created_at')

#     # Mark as read
#     new_msgs.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

#     msgs_data = []
#     for msg in new_msgs:
#         emp      = get_employee_or_none(msg.sender)
#         initials = ''
#         if emp:
#             initials = f"{emp.first_name[0]}{emp.last_name[0]}".upper()
#         else:
#             initials = msg.sender.username[:2].upper()

#         msgs_data.append({
#             'id':       msg.id,
#             'content':  msg.content,
#             'sender':   msg.sender.get_full_name() or msg.sender.username,
#             'initials': initials,
#             'photo':    emp.photo.url if emp and emp.photo else None,
#             'time':     msg.created_at.strftime('%I:%M %p'),
#             'is_mine':  msg.sender == request.user,
#         })

#     return JsonResponse({'messages': msgs_data})


# # ── Unread Count (AJAX) ───────────────────────────────────────────────────────
# @login_required
# def unread_count(request):
#     count = Message.objects.filter(
#         conversation__participants=request.user,
#         is_read=False
#     ).exclude(sender=request.user).count()
#     return JsonResponse({'count': count})


# # ── Create Group Chat ─────────────────────────────────────────────────────────
# @login_required
# def create_group(request):
#     if request.method == 'POST':
#         name        = request.POST.get('name', '').strip()
#         member_ids  = request.POST.getlist('members')

#         if not name:
#             from django.contrib import messages
#             messages.error(request, 'Group name is required.')
#             return redirect('chat_home')

#         conv = Conversation.objects.create(
#             conv_type='group',
#             name=name,
#             created_by=request.user,
#         )
#         conv.participants.add(request.user)
#         for uid in member_ids:
#             try:
#                 user = User.objects.get(pk=uid)
#                 conv.participants.add(user)
#             except User.DoesNotExist:
#                 pass

#         # Welcome message
#         Message.objects.create(
#             conversation=conv,
#             sender=request.user,
#             content=f"🎉 Group '{name}' created! Welcome everyone.",
#         )

#         return redirect('chat_room', conv_id=conv.id)

#     return redirect('chat_home')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count
from django.utils import timezone
import json
from .models import Conversation, Message
from employees.models import Employee


def get_employee_or_none(user):
    try:
        return Employee.objects.select_related('department', 'designation').get(user=user)
    except Employee.DoesNotExist:
        return None


def _base_template(user):
    """HR/admin users get the admin shell, everyone else (employees) get the portal shell."""
    return 'base.html' if (user.is_staff or user.is_superuser) else 'portal/base_portal.html'

# Emoji picker options (chat_home.html loops over this to render the picker)
EMOJI_LIST = [
    '😀', '😂', '😊', '😍', '😎', '🤔', '😅', '😢', '😡', '👍',
    '👎', '👏', '🙏', '🔥', '🎉', '❤️', '💯', '✅', '❌', '🚀',
    '😴', '🤝', '👋', '💪', '😁', '🙌', '🥳', '😇', '🤷', '📌',
]

# ── Chat Home ─────────────────────────────────────────────────────────────────
@login_required
def chat_home(request):
    # Get all conversations for current user
    conversations = Conversation.objects.filter(
        participants=request.user
    ).prefetch_related('participants').order_by('-updated_at')

    # Annotate with unread count
    conv_data = []
    for conv in conversations:
        last_msg    = conv.last_message()
        unread      = conv.messages.filter(is_read=False).exclude(sender=request.user).count()
        other_user  = conv.get_other_participant(request.user)
        other_emp   = get_employee_or_none(other_user) if other_user else None

        conv_data.append({
            'conv':       conv,
            'last_msg':   last_msg,
            'unread':     unread,
            'other_user': other_user,
            'other_emp':  other_emp,
        })

    # All employees for new chat — every active employee, HR or not,
    # so any individual can start a 1:1 chat with any colleague.
    all_employees = Employee.objects.filter(
        status='active'
    ).select_related('user', 'department', 'designation').exclude(user=request.user)

    current_emp = get_employee_or_none(request.user)
    total_unread = sum(c['unread'] for c in conv_data)

    return render(request, 'messaging/chat_home.html', {
        'conv_data':     conv_data,
        'all_employees': all_employees,
        'current_emp':   current_emp,
        'total_unread':  total_unread,
        'base_template': _base_template(request.user),
        'emoji_list':    EMOJI_LIST, 
        
    })


# ── Open / Start DM ───────────────────────────────────────────────────────────
@login_required
def open_chat(request, user_id):
    other_user = get_object_or_404(User, pk=user_id)

    # Find existing DM conversation
    conv = Conversation.objects.filter(
        conv_type='direct',
        participants=request.user
    ).filter(
        participants=other_user
    ).first()

    # Create new if not exists
    if not conv:
        conv = Conversation.objects.create(
            conv_type='direct',
            created_by=request.user
        )
        conv.participants.add(request.user, other_user)

    return redirect('chat_room', conv_id=conv.id)


# ── Chat Room ─────────────────────────────────────────────────────────────────
@login_required
def chat_room(request, conv_id):
    conv = get_object_or_404(Conversation, id=conv_id, participants=request.user)

    # Mark messages as read
    conv.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    # messages_list = conv.messages.select_related('sender').order_by('created_at')

    # # Har message ke sender ki photo/initials attach karein (chat bubble avatar ke liye)
    # for msg in messages_list:
    #     sender_emp = get_employee_or_none(msg.sender)
    #     msg.sender_emp = sender_emp
    #     if sender_emp:
    #         msg.sender_photo_url = sender_emp.photo.url if sender_emp.photo else None
    #         msg.sender_initials  = f"{sender_emp.first_name[0]}{sender_emp.last_name[0]}".upper()
    #     else:
    #         msg.sender_photo_url = None
    #         msg.sender_initials  = msg.sender.username[:2].upper()

    messages_list = conv.messages.select_related('sender').order_by('created_at')

    # Har message ke sender ki photo/initials attach karein (chat bubble avatar ke liye)
    prev_sender = None
    for msg in messages_list:
        sender_emp = get_employee_or_none(msg.sender)
        msg.sender_emp = sender_emp
        if sender_emp:
            msg.sender_photo_url = sender_emp.photo.url if sender_emp.photo else None
            msg.sender_initials  = f"{sender_emp.first_name[0]}{sender_emp.last_name[0]}".upper()
        else:
            msg.sender_photo_url = None
            msg.sender_initials  = msg.sender.username[:2].upper()

        msg.show_header = (msg.sender_id != prev_sender)
        prev_sender = msg.sender_id

    # All conversations for sidebar
    conversations = Conversation.objects.filter(
        participants=request.user
    ).prefetch_related('participants').order_by('-updated_at')

    conv_data = []
    for c in conversations:
        last_msg   = c.last_message()
        unread     = c.messages.filter(is_read=False).exclude(sender=request.user).count()
        other_user = c.get_other_participant(request.user)
        other_emp  = get_employee_or_none(other_user) if other_user else None
        conv_data.append({
            'conv': c, 'last_msg': last_msg,
            'unread': unread, 'other_user': other_user, 'other_emp': other_emp,
            'is_active': c.id == conv.id,
        })

    other_user = conv.get_other_participant(request.user)
    other_emp  = get_employee_or_none(other_user) if other_user else None
    current_emp = get_employee_or_none(request.user)
    all_employees = Employee.objects.filter(
        status='active'
    ).select_related('user', 'department').exclude(user=request.user)

    return render(request, 'messaging/chat_home.html', {
        'conv':          conv,
        'messages_list': messages_list,
        'conv_data':     conv_data,
        'other_user':    other_user,
        'other_emp':     other_emp,
        'current_emp':   current_emp,
        'all_employees': all_employees,
        'base_template': _base_template(request.user),
        'emoji_list':    EMOJI_LIST,
    })


# ── Send Message (AJAX) ───────────────────────────────────────────────────────
@login_required
def send_message(request, conv_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    conv = get_object_or_404(Conversation, id=conv_id, participants=request.user)
    content = request.POST.get('content', '').strip()

    if not content:
        return JsonResponse({'error': 'Empty message'}, status=400)

    msg = Message.objects.create(
        conversation=conv,
        sender=request.user,
        content=content,
    )

    # Update conversation timestamp
    conv.updated_at = timezone.now()
    conv.save(update_fields=['updated_at'])

    emp = get_employee_or_none(request.user)
    initials = ''
    if emp:
        initials = f"{emp.first_name[0]}{emp.last_name[0]}".upper()
    else:
        initials = request.user.username[:2].upper()

    return JsonResponse({
        'id':         msg.id,
        'content':    msg.content,
        'sender':     request.user.get_full_name() or request.user.username,
        'sender_id':  request.user.id, 
        'initials':   initials,
        'photo':      emp.photo.url if emp and emp.photo else None,
        'time':       msg.created_at.strftime('%I:%M %p'),
        'is_mine':    True,
    })


# ── Poll New Messages (AJAX) ──────────────────────────────────────────────────
@login_required
def poll_messages(request, conv_id):
    conv        = get_object_or_404(Conversation, id=conv_id, participants=request.user)
    last_id     = int(request.GET.get('last_id', 0))
    new_msgs    = conv.messages.filter(id__gt=last_id).select_related('sender').order_by('created_at')

    # Mark as read
    new_msgs.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    msgs_data = []
    for msg in new_msgs:
        emp      = get_employee_or_none(msg.sender)
        initials = ''
        if emp:
            initials = f"{emp.first_name[0]}{emp.last_name[0]}".upper()
        else:
            initials = msg.sender.username[:2].upper()

        msgs_data.append({
            'id':       msg.id,
            'content':  msg.content,
            'sender':   msg.sender.get_full_name() or msg.sender.username,
            'sender_id': msg.sender_id,
            'initials': initials,
            'photo':    emp.photo.url if emp and emp.photo else None,
            'time':     msg.created_at.strftime('%I:%M %p'),
            'is_mine':  msg.sender == request.user,
        })

    return JsonResponse({'messages': msgs_data})


# ── Unread Count (AJAX) ───────────────────────────────────────────────────────
@login_required
def unread_count(request):
    count = Message.objects.filter(
        conversation__participants=request.user,
        is_read=False
    ).exclude(sender=request.user).count()
    return JsonResponse({'count': count})


# ── Conversation List (AJAX, for live sidebar refresh) ────────────────────────
@login_required
def conv_list_json(request):
    conversations = Conversation.objects.filter(
        participants=request.user
    ).prefetch_related('participants').order_by('-updated_at')

    data = []
    total_unread = 0
    for conv in conversations:
        last_msg = conv.last_message()
        unread   = conv.messages.filter(is_read=False).exclude(sender=request.user).count()
        total_unread += unread

        other_user = conv.get_other_participant(request.user)
        other_emp  = get_employee_or_none(other_user) if other_user else None

        if conv.conv_type == 'group':
            name = conv.name
        elif other_emp:
            name = other_emp.full_name
        else:
            name = other_user.username if other_user else 'Unknown'

        last_text = ''
        last_time = ''
        if last_msg:
            prefix = 'You: ' if last_msg.sender_id == request.user.id else ''
            last_text = (prefix + last_msg.content)[:60]
            last_time = last_msg.created_at.strftime('%H:%M')

        data.append({
            'id':        conv.id,
            'name':      name,
            'last_text': last_text or 'Start a conversation',
            'last_time': last_time,
            'unread':    unread,
        })

    return JsonResponse({'conversations': data, 'total_unread': total_unread})


# ── Create Group Chat ─────────────────────────────────────────────────────────
@login_required
def create_group(request):
    if request.method == 'POST':
        name        = request.POST.get('name', '').strip()
        member_ids  = request.POST.getlist('members')

        if not name:
            from django.contrib import messages
            messages.error(request, 'Group name is required.')
            return redirect('chat_home')

        conv = Conversation.objects.create(
            conv_type='group',
            name=name,
            created_by=request.user,
        )
        conv.participants.add(request.user)
        for uid in member_ids:
            try:
                user = User.objects.get(pk=uid)
                conv.participants.add(user)
            except User.DoesNotExist:
                pass

        # Welcome message
        Message.objects.create(
            conversation=conv,
            sender=request.user,
            content=f"🎉 Group '{name}' created! Welcome everyone.",
        )

        return redirect('chat_room', conv_id=conv.id)

    return redirect('chat_home')