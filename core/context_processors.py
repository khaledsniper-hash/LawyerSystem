# ========================================
# Context Processors - Mizan Al-Adala
# ========================================

def notification_count(request):
    """
    إضافة عدد الإشعارات غير المقروءة لجميع القوالب
    """
    try:
        from core.models import Notification
        if request.user.is_authenticated:
            count = Notification.objects.filter(
                user=request.user,
                is_read=False
            ).count()
        else:
            count = 0
    except:
        count = 0  # في حالة عدم وجود نموذج Notification
    
    return {'notification_count': count}


def office_profile(request):
    """
    إضافة بيانات المكتب (الاسم، الشعار) لجميع القوالب
    """
    try:
        from core.models import OfficeProfile
        profile = OfficeProfile.objects.first()
    except:
        profile = None
    
    return {'office_profile': profile}