from django.conf import settings


def calendar_analytics_processor(request):

    return {
            'social_auth_google_plus_key': settings.SOCIAL_AUTH_GOOGLE_PLUS_KEY,
            # Space separated string of scopes
            'social_auth_google_oauth2_scope': " ".join(map(str, settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE)),
            }
