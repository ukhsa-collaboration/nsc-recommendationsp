from django.core.signing import Signer


def get_value_to_sign(obj):
    return str(obj.id)


def get_object_signature(obj):
    signer = Signer()
    return signer.signature(get_value_to_sign(obj))


def check_object(obj, signature):
    signer = Signer()
    value = get_value_to_sign(obj)

    # manually recompute signature and compare
    expected_signature = signer.signature(value)
    return signature == expected_signature
