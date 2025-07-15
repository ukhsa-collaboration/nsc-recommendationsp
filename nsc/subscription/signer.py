from django.core.signing import BadSignature, Signer


def get_value_to_sign(obj):
    return str(obj.id)


def get_object_signature(obj):
    signer = Signer()
    return signer.signature(get_value_to_sign(obj))


def check_object(obj, signature):
    signer = Signer()
    value = get_value_to_sign(obj)

    try:
        return signer.unsign(f"{value}:{signature}") == value  # noqa
    except BadSignature:
        return False
