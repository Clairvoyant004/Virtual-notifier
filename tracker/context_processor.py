from .models import League

def leagues_nav(request):
    return {
        "all_leagues": League.objects.all().order_by("external_id")
    }
