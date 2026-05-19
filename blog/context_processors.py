from .models import SavedPost, SiteSettings


def reading_stats(request):
    if request.user.is_authenticated:
        return {
            'nav_saved_count': SavedPost.objects.filter(user=request.user).count(),
        }
    return {'nav_saved_count': 0}


def site_settings(request):
    return {'site_settings': SiteSettings.get_solo()}
