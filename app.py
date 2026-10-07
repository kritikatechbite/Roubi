
from flask import Flask, render_template, request, redirect, abort, session
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from datetime import datetime
import os

app = Flask(__name__)

# IMPORTANT:
# Keep secrets and destination URLs in environment variables on the host.
# Do not put real production URLs in templates or JavaScript.
app.secret_key = os.getenv("APP_SECRET_KEY", "change-this-in-production")

DESKTOP_DESTINATION_URL = os.getenv("DESKTOP_DESTINATION_URL", "").strip()
MOBILE_DESTINATION_URL = os.getenv("MOBILE_DESTINATION_URL", "").strip()

serializer = URLSafeTimedSerializer(app.secret_key, salt="roubi-toy-continue")

def is_mobile_request():
    ua = (request.headers.get("User-Agent") or "").lower()
    mobile_terms = ("android", "iphone", "ipad", "ipod", "mobile", "opera mini", "iemobile")
    return any(term in ua for term in mobile_terms)

def make_continue_token():
    # Token proves that the visitor first loaded our page.
    # It does not identify bots and is not used for cloaking.
    return serializer.dumps({"purpose": "continue"})

def validate_continue_token(token):
    try:
        data = serializer.loads(token, max_age=900)
        return data.get("purpose") == "continue"
    except (BadSignature, SignatureExpired):
        return False

@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' https://images.unsplash.com data:; "
        "style-src 'self' https://fonts.googleapis.com 'unsafe-inline'; "
        "font-src https://fonts.gstatic.com; "
        "script-src 'self'; "
        "base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
    )
    return response

@app.context_processor
def inject_common():
    return {"year": datetime.now().year}

@app.route("/")
def home():
    return render_template(
        "index.html",
        page="home",
        continue_token=make_continue_token()
    )

@app.route("/reviews")
def reviews():
    return render_template(
        "reviews.html",
        page="reviews",
        continue_token=make_continue_token()
    )

@app.route("/about")
def about():
    return render_template("about.html", page="about")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html", page="privacy")

@app.route("/terms")
def terms():
    return render_template("terms.html", page="terms")

@app.post("/continue")
def continue_route():
    token = request.form.get("token", "")
    if not validate_continue_token(token):
        abort(403)

    destination = MOBILE_DESTINATION_URL if is_mobile_request() else DESKTOP_DESTINATION_URL

    if not destination:
        return render_template("not-configured.html"), 503

    return redirect(destination, code=302)

@app.route("/robots.txt")
def robots():
    # Search engines may crawl the public content.
    # The redirect destinations are not listed here or in HTML.
    return "User-agent: *\nAllow: /\n", 200, {"Content-Type":"text/plain; charset=utf-8"}

if __name__ == "__main__":
    app.run(debug=False)
