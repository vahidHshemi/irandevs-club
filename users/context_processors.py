from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def notificationCount(request):
    profile = request.user.profile
    messageRequests = profile.messages.all()
    unreadCount = messageRequests.filter(is_read=False).count()
    return {'unreadCount': unreadCount}
