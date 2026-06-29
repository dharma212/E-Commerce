from User.models import AdminNotification

def dashboard_notifications(request):
    if "dashboard_user_id" in request.session:
        notifications = AdminNotification.objects.all().order_by('-created_at')[:5]
        unread_count = AdminNotification.objects.filter(is_read=False).count()
        return {
            'notifications': notifications,
            'unread_count': unread_count
        }
    
    return {
        'notifications': [],
        'unread_count': 0
    }