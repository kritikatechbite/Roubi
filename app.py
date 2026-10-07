from flask import Flask, render_template, request, redirect, abort
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from datetime import datetime
import os

app = Flask(__name__)

# Keep secrets and destination URLs in environment variables.
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


serializer = URLSafeTimedSerializer(
    app.secret_key,
    salt="roubi-toy-continue"
)


def is_mobile_request():
    ua = (request.headers.get("User-Agent") or "").lower()

    mobile_terms = (
        "android",
        "iphone",
        "ipad",
        "ipod",
        "mobile",
        "opera mini",
        "iemobile"
    )

    return any(term in ua for term in mobile_terms)


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
    ] = "camera=(), microphone=(), geolocation=()"

    response.headers[
        "Content-Security-Policy"
    ] = (
        "default-src 'self'; "
        "img-src 'self' https://images.unsplash.com data:; "
        "style-src 'self' https://fonts.googleapis.com 'unsafe-inline'; "
        "font-src https://fonts.gstatic.com; "
        "script-src 'self'; "
        "base-uri 'self'; "
        "frame-ancestors 'none'; "
        "form-action 'self'"
    )

    return response


@app.context_processor
def inject_common():

    return {
        "year": datetime.now().year
    }


# =========================
# HOME
# =========================

@app.route("/")
def home():

    return render_template(
        "index.html",
        page="home",
        continue_token=make_continue_token()
    )


# =========================
# REVIEWS PAGE
# =========================

@app.route("/reviews")
def reviews():

    return render_template(
        "reviews.html",
        page="reviews",
        continue_token=make_continue_token()
    )


# =========================
# ABOUT
# =========================

@app.route("/about")
def about():

    return render_template(
        "about.html",
        page="about"
    )


# =========================
# PRIVACY
# =========================

@app.route("/privacy")
def privacy():

    return render_template(
        "privacy.html",
        page="privacy"
    )


# =========================
# TERMS
# =========================

@app.route("/terms")
def terms():

    return render_template(
        "terms.html",
        page="terms"
    )


# =========================
# REVIEW URL
#
# Desktop:
# /review -> normal website
#
# Mobile:
# /review -> MOBILE_DESTINATION_URL
# =========================

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


    # Desktop visitors see normal website

    return render_template(
        "index.html",
        page="home",
        continue_token=make_continue_token()
    )


# =========================
# EXISTING CONTINUE FLOW
# =========================

@app.post("/continue")
def continue_route():

    token = request.form.get(
        "token",
        ""
    )

    if not validate_continue_token(token):

        abort(403)


    if is_mobile_request():

        destination = MOBILE_DESTINATION_URL

    else:

        destination = DESKTOP_DESTINATION_URL


    if not destination:

        return render_template(
            "not-configured.html"
        ), 503


    return redirect(
        destination,
        code=302
    )


# =========================
# ROBOTS
# =========================

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


# =========================
# RUN
# =========================

if __name__ == "__main__":

    app.run(
        debug=False
    )
