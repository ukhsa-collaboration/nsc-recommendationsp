def record_user_session(get_response):
    def handler(request):
        if (
            request.user.is_authenticated
            and request.user.last_session_id != request.session.session_key
        ):
            request.user.last_session_id = request.session.session_key
            request.user.save()

        return get_response(request)

    return handler
