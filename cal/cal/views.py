from cal.models import GoogleCredentials, GoogleFlow, Profile, Category, Tag

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from oauth2client.client import OAuth2WebServerFlow, AccessTokenCredentials
from oauth2client.django_orm import Storage

from social.apps.django_app.utils import psa


@ensure_csrf_cookie
def home(request):
    inc_sync_flag = False
    if request.user.is_authenticated():
        if not request.GET.get('no_sync') and inc_sync_flag:
            return HttpResponseRedirect("/v1/sync?sync_all=true")
        else:
            return render(request, template_name='home_logged_in.html')
    else:
        return render(request, template_name='home_logged_out.html')

def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")

@login_required
def clear_auth(request):
    """
    Clears the credentials for the requesting user
    """
    if request.user:
        profile, _ = Profile.get_or_create(user=request.user)
        profile.clear_credentials()
    return HttpResponseRedirect("/")

@login_required
def generate_categories(request):
    request.user.profile.generate_categories()
    return HttpResponseRedirect("/")

@login_required
def accounts_profile(request):
    """
    Shows the account information for a user
    For now, redirects to homepage.
    """
    # TODO either remove this view or change Python Social Auth after login
    return HttpResponseRedirect("/")

@csrf_exempt
@psa('social:complete')
def complete_with_token(request, backend):
    # This view expects an access_token POST parameter, if it's needed,
    # request.backend and request.strategy will be loaded with the current
    # backend and strategy.
    token = request.POST.get('access_token')
    print "Token: {}".format(token)
    user = request.backend.do_auth(token)
    if user:
        login(request, user)

        # The user agent is only used for logs
        credential = AccessTokenCredentials(token, 'dummy-user-agent/1.0')
        storage = Storage(GoogleCredentials, 'user', request.user, 'credential')
        storage.put(credential)

    return HttpResponseRedirect("/")

@login_required
def google_auth(request):
    """
    Handles Google oauth flow. For details, visit
    https://developers.google.com/api-client-library/python/guide/aaa_oauth#OAuth2WebServerFlow
    https://developers.google.com/api-client-library/python/guide/django
    """

    flow = None

    default_flow = OAuth2WebServerFlow(client_id=settings.GOOGLE_CALENDAR_API_CLIENT_ID,
                                       client_secret=settings.GOOGLE_CALENDAR_API_CLIENT_SECRET,
                                       scope=['https://www.googleapis.com/auth/calendar','profile','email'],
                                       redirect_uri='https://calendarapptest.herokuapp.com/auth/google')
    default_flow.params['access_type'] = 'offline'
    default_flow.params['include_granted_scopes'] = 'true'
    default_flow.params['prompt'] = 'consent'

    # Try to retrieve an existing flow, or create one if it doesn't exist
    gflow = GoogleFlow.objects.filter(id=request.user).last()

    if gflow and gflow.flow.params.get('prompt') != 'consent':
        # Delete any flows that don't have the prompt parameter set, since that will
        # prevent the credentials from getting a refresh token
        gflow.delete()
        gflow = None

    if not gflow:
        print "Could not retrieve existing flow"
        gflow = GoogleFlow(id=request.user,
                          flow=default_flow)
        gflow.save()
    gflow = GoogleFlow(id=request.user,
                      flow=default_flow)
    flow = gflow.flow

    code = request.GET.get('code', None)
    error = request.GET.get('error', None)
    print flow
    print flow.params

    if error:
        # TODO eventually make this prettier, like redirect to some landing page
        return HttpResponseBadRequest("Authentication failed. Reason: {}".format(error))
    elif code:
        print 'entered code'
        credential = flow.step2_exchange(code)
        # Save the credentials
        storage = Storage(GoogleCredentials, 'user', request.user, 'credential')
        storage.put(credential)
        profile, _ = Profile.get_or_create(user=request.user)
        profile.authed = True
        profile.save()

        # TODO improve the latency over here
        request.user.googlecredentials.import_calendars()

        return HttpResponseRedirect("/")
    else:
        auth_uri = flow.step1_get_authorize_url()
        return HttpResponseRedirect(auth_uri)


def handler404(request):
    response = render('404.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response
