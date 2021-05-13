import gunicorn


gunicorn.SERVER_SOFTWARE = "a-web-server-af309666-dfc3-4296-8211-cf6871f4c227"
workers = 4
threads = 4
bind = "0.0.0.0:8080"
error_logfile = "-"
access_logfile = "-"
