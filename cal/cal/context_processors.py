from django.conf import settings


def google_client_id_processor(request):

    return {'google_client_id': settings.GOOGLE_CALENDAR_API_CLIENT_ID}
