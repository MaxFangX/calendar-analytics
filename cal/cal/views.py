from cal.models import GoogleCredentials, GoogleFlow

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_POST

from oauth2client.client import OAuth2WebServerFlow
from oauth2client.django_orm import Storage


def home(request):
    if request.user.is_authenticated():
        return render_to_response(template_name='home_logged_in.html')

    context = RequestContext(request, {
        'google_client_id': settings.GOOGLE_CALENDAR_API_CLIENT_ID,
        'base_url': settings.BASE_URL,
    })

    return render_to_response(template_name='home_logged_out.html',
                              context=context)


@require_POST
def login_view(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)

    context_instance = RequestContext(request)

    if user is not None:
        login(request, user)
        return render_to_response(template_name='home_logged_in.html', context_instance=context_instance)
    else:
        return HttpResponse("Failed to log in.")


def logout_view(request):
    logout(request)
    return render_to_response(template_name='home_logged_out.html')


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
                                       redirect_uri=settings.BASE_URL + '/auth/google')

    # TODO perhaps create a new user upon oauth, to skip this check
    if request.user.is_authenticated():
        # Try to retrieve an existing flow, or create one if it doesn't exist
        gflow = GoogleFlow.objects.filter(id=request.user).last()
        if not gflow:
            gflow = GoogleFlow(id=request.user,
                              flow=default_flow)
            gflow.save()
        flow = gflow.flow
    else:
        flow = default_flow

    code = request.GET.get('code', None)
    error = request.GET.get('error', None)

    if error:
        # TODO eventually make this prettier, like redirect to some landing page
        return HttpResponseBadRequest("Authentication failed. Reason: {}".format(error))
    elif code:
        credentials = flow.step2_exchange(code)
        if request.user.is_authenticated():
            # Save the credentials
            storage = Storage(GoogleCredentials, 'id', request.user, 'credential')
            storage.put(credentials)

        return HttpResponseRedirect("/")
    else:
        auth_uri = flow.step1_get_authorize_url()
        return HttpResponseRedirect(auth_uri)


def complete_google(request):
    """
    Completes the Google oauth flow. For details, visit
    https://developers.google.com/api-client-library/python/guide/aaa_oauth#OAuth2WebServerFlow
    https://developers.google.com/api-client-library/python/guide/django
    """
    # TODO implement auth completion
    return HttpResponse(status=200)
