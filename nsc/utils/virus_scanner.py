import clamd

def is_file_clean(file):
    """
    Scans the uploaded file using ClamAV.
    Returns True if clean, False if malware detected (or scanning fails).
    """
    try:
        cd = clamd.ClamdUnixSocket()
    except Exception as e:
        print(f"Error connecting to clamd: {e}")
        return False

    file.seek(0)
    try:
        result = cd.instream(file)
        status, reason = result.get('stream', ('ERROR', None))
        return status == 'OK'
    except Exception as e:
        print(f"Error scanning file: {e}")
        return False