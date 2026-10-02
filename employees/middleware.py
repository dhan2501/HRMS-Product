from django.utils import timezone

# Only touch the DB once every this many seconds per user, so normal
# page loads / AJAX polling don't hammer the database on every request.
UPDATE_INTERVAL_SECONDS = 30


class UpdateLastSeenMiddleware:
    """
    Stamps Employee.last_seen for the logged-in user on every authenticated
    request. This is what drives real Online/Offline status in chat —
    without it, "online" was just a hardcoded label, not an actual login
    check.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            now = timezone.now()
            last_update = request.session.get('_last_seen_update')
            should_update = (
                last_update is None
                or (now.timestamp() - last_update) >= UPDATE_INTERVAL_SECONDS
            )
            if should_update:
                # Avoid a circular import at module load time.
                from employees.models import Employee
                Employee.objects.filter(user_id=user.id).update(last_seen=now)
                request.session['_last_seen_update'] = now.timestamp()

        return response