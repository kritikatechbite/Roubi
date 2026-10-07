
from flask import Flask, render_template, redirect
from datetime import datetime
import os

app = Flask(__name__)

# =========================================================
# REDIRECT URL
# =========================================================
# Do NOT hard-code your production link in templates or JS.
# Set REDIRECT_URL in Belmo -> Environment Variables.
REDIRECT_URL = os.getenv("REDIRECT_URL", "").strip()


# =========================================================
# SECURITY HEADERS
# =========================================================
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
        "base-uri 'self'; "
        "frame-ancestors 'none'"
    )
    return response


@app.context_processor
def inject_common():
    return {
        "year": datetime.now().year
    }


# =========================================================
# NORMAL WEBSITE ROUTES
# =========================================================
@app.route("/")
def home():
    return render_template(
        "index.html",
        page="home"
    )

@app.route("/reviews")
def reviews():
    return render_template(
        "reviews.html",
        page="reviews"
    )


@app.route("/about")
def about():
    return render_template(
        "about.html",
        page="about"
    )


@app.route("/privacy")
def privacy():
    return render_template(
        "privacy.html",
        page="privacy"
    )


@app.route("/terms")
def terms():
    return render_template(
        "terms.html",
        page="terms"
    )


# =========================================================
# REVIEW REDIRECT
#
# Normal domain:
# https://your-domain.com/
# -> Roubi Toy Company website
#
# Review slug:
# https://your-domain.com/review
# -> REDIRECT_URL
#
# Same redirect for desktop and mobile.
# =========================================================
@app.route("/review")
def review():
    if REDIRECT_URL:
        return redirect(REDIRECT_URL, code=302)

    return render_template("not-configured.html"), 503

# =========================================================
# SIMPLE HEALTH CHECK
# =========================================================
@app.route("/health")
def health():
    return {
        "status": "ok",
        "redirect_configured": bool(REDIRECT_URL)
    }


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
            "Content-Type": "text/plain; charset=utf-8"
        }
    )


# =========================================================
# LOCAL RUN
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
