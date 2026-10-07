from flask import Flask, render_template, request, redirect, abort
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from datetime import datetime
import os

app = Flask(__name__)


# =========================================================
# ENVIRONMENT VARIABLES
# =========================================================

app.secret_key = os.getenv(
    "APP_SECRET_KEY",
    "change-this-in-production"
)

DESKTOP_DESTINATION_URL = os.getenv(
    "DESKTOP_DESTINATION_URL",
    ""
).strip()

MOBILE_DESTINATION_URL = os.getenv(
    "MOBILE_DESTINATION_URL",
    ""
).strip()


# =========================================================
# SIGNED TOKEN
# =========================================================

serializer = URLSafeTimedSerializer(
    app.secret_key,
    salt="roubi-toy-continue"
)


def make_continue_token():
    return serializer.dumps({
        "purpose": "continue"
    })


def validate_continue_token(token):
    try:
        data = serializer.loads(
            token,
            max_age=900
        )

        return data.get("purpose") == "continue"

    except (BadSignature, SignatureExpired):
        return False


# =========================================================
# MOBILE DETECTION
# =========================================================

def is_mobile_request():

    # Modern Chromium browsers may send:
    # Sec-CH-UA-Mobile: ?1
    client_hint = request.headers.get(
        "Sec-CH-UA-Mobile",
        ""
    ).strip()

    if client_hint == "?1":
        return True


    # Fallback to User-Agent detection
    ua = (
        request.headers.get(
            "User-Agent"
        )
        or ""
    ).lower()


    mobile_terms = (
        "android",
        "iphone",
        "ipad",
        "ipod",
        "mobile",
        "opera mini",
        "iemobile",
        "blackberry",
        "webos"
    )


    return any(
        term in ua
        for term in mobile_terms
    )


# =========================================================
# SECURITY HEADERS
# =========================================================

@app.after_request
def security_headers(response):

    response.headers[
        "X-Content-Type-Options"
    ] = "nosniff"

    response.headers[
        "X-Frame-Options"
    ] = "DENY"

    response.headers[
        "Referrer-Policy"
    ] = "strict-origin-when-cross-origin"

    response.headers[
        "Permissions-Policy"
    ] = (
        "camera=(), "
        "microphone=(), "
        "geolocation=()"
    )

    response.headers[
        "Content-Security-Policy"
    ] = (
        "default-src 'self'; "
        "img-src 'self' https://images.unsplash.com data:; "
        "style-src 'self' "
        "https://fonts.googleapis.com "
        "'unsafe-inline'; "
        "font-src https://fonts.gstatic.com; "
        "script-src 'self'; "
        "base-uri 'self'; "
        "frame-ancestors 'none'; "
        "form-action 'self'"
    )

    return response


# =========================================================
# GLOBAL TEMPLATE DATA
# =========================================================

@app.context_processor
def inject_common():

    return {
        "year": datetime.now().year
    }


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html",
        page="home",
        continue_token=make_continue_token()
    )


# =========================================================
# REVIEWS
# =========================================================

@app.route("/reviews")
def reviews():

    return render_template(
        "reviews.html",
        page="reviews",
        continue_token=make_continue_token()
    )


# =========================================================
# ABOUT
# =========================================================

@app.route("/about")
def about():

    return render_template(
        "about.html",
        page="about"
    )


# =========================================================
# PRIVACY
# =========================================================

@app.route("/privacy")
def privacy():

    return render_template(
        "privacy.html",
        page="privacy"
    )


# =========================================================
# TERMS
# =========================================================

@app.route("/terms")
def terms():

    return render_template(
        "terms.html",
        page="terms"
    )


# =========================================================
# REVIEW ROUTE
#
# Desktop:
# /review -> normal website
#
# Mobile:
# /review -> MOBILE_DESTINATION_URL
# =========================================================

@app.route("/review")
def review():

    if is_mobile_request():

        if MOBILE_DESTINATION_URL:

            return redirect(
                MOBILE_DESTINATION_URL,
                code=302
            )


        return render_template(
            "not-configured.html"
        ), 503


    # Desktop visitors stay on normal website

    return render_template(
        "index.html",
        page="home",
        continue_token=make_continue_token()
    )


# =========================================================
# DEVICE CHECK
#
# Temporary debugging route.
# Open /device-check on your real phone.
# =========================================================

@app.route("/device-check")
def device_check():

    return {

        "mobile":
            is_mobile_request(),

        "tracking_set":
            bool(MOBILE_DESTINATION_URL),

        "desktop_tracking_set":
            bool(DESKTOP_DESTINATION_URL),

        "client_hint":
            request.headers.get(
                "Sec-CH-UA-Mobile"
            ),

        "user_agent":
            request.headers.get(
                "User-Agent"
            )
    }


# =========================================================
# EXISTING CONTINUE FLOW
# =========================================================

@app.post("/continue")
def continue_route():

    token = request.form.get(
        "token",
        ""
    )


    if not validate_continue_token(
        token
    ):

        abort(403)


    if is_mobile_request():

        destination = (
            MOBILE_DESTINATION_URL
        )

    else:

        destination = (
            DESKTOP_DESTINATION_URL
        )


    if not destination:

        return render_template(
            "not-configured.html"
        ), 503


    return redirect(
        destination,
        code=302
    )


# =========================================================
# ROBOTS.TXT
# =========================================================

@app.route("/robots.txt")
def robots():

    return (
        "User-agent: *\n"
        "Allow: /\n",
        200,
        {
            "Content-Type":
            "text/plain; charset=utf-8"
        }
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    return {
        "status": "ok"
    }


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(
            os.getenv(
                "PORT",
                "5000"
            )
        ),
        debug=False
    )
