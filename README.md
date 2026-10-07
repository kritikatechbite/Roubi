
# Roubi Toy Company — Server-side redirect version

This project is a Flask website for toy reviews, play ideas and family buying guides.

The destination URLs are kept server-side in environment variables and are not embedded in the HTML or JavaScript.

## Environment variables

APP_SECRET_KEY
DESKTOP_DESTINATION_URL
MOBILE_DESTINATION_URL

The `/continue` route uses a short-lived signed token and then selects the configured mobile or desktop destination based on the requesting device.

## PythonAnywhere

Project folder:
`/home/YOURUSERNAME/Roubi_Toy_Company`

Virtualenv example:
`roubi-toy-env`

Install:
`pip install -r requirements.txt`

WSGI example:

```python
import os, sys

project_path = '/home/YOURUSERNAME/Roubi_Toy_Company'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.environ["APP_SECRET_KEY"] = "CHANGE-ME"
os.environ["DESKTOP_DESTINATION_URL"] = "https://example.com/desktop"
os.environ["MOBILE_DESTINATION_URL"] = "https://example.com/mobile"

from app import app as application
```

Static mapping:
URL: `/static/`
Directory: `/home/YOURUSERNAME/Roubi_Toy_Company/static/`
