from urllib.parse import urlparse

from django.http import HttpResponseRedirect


def redirect_url_fragment(get_response):
    """
    Sets the fragment of the redirect urls
    """

    def redirection(request):
        response = get_response(request)

        if (
            isinstance(response, HttpResponseRedirect)
            and not urlparse(response.url).fragment
        ):
            return HttpResponseRedirect(f"{response.url}#")

        return response

    return redirection
