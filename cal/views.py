from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from oauth2client.client import OAuth2WebServerFlow


def home(request):
    if request.user.is_authenticated():
        return render_to_response(template_name='home_logged_in.html')
    return render_to_response(template_name='home_logged_out.html')


def logout_view(request):
    logout(request)
    return render_to_response(template_name='home_logged_out.html')


def google_auth(request):
    if request.POST:
        pass

    flow = OAuth2WebServerFlow(client_id=settings.GOOGLE_CALENDAR_API_CLIENT_ID,
                               client_secret=settings.GOOGLE_CALENDAR_API_CLIENT_SECRET,
                               scope='https://www.googleapis.com/auth/calendar',
                               redirect_uri=settings.BASE_URL + '/auth/google')

    auth_uri = flow.step1_get_authorize_url()
    return HttpResponseRedirect(auth_uri)
