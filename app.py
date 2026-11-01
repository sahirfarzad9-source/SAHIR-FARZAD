"""
╔══════════════════════════════════════════════════════════════╗
║  LESSON 4 — Building Dynamic Sneaker Requests with JSON/Fetch║
╚══════════════════════════════════════════════════════════════╝

GOAL: Add HuggingFace FLUX image generation. After the concept
      loads, the browser fetches the AI image asynchronously.

YOUR TASKS (app.py):
  1. Add HF_API_KEY and HF_IMAGE_URL constants
  2. Write hex_to_color_name(h) — converts "#1a1a2e" → "dark blue"
     using brightness and dominant channel logic
  3. Write generate_sneaker_image(prompt) — POST to HF_IMAGE_URL,
     return base64 data URL on success, None on failure
  4. Write build_image_prompt(prefs) — builds a descriptive FLUX
     prompt using hex_to_color_name() for colors
  5. Add /generate-image POST route — calls generate_sneaker_image,
     returns {"success": True, "image_url": ...}
  6. In /generate: attach image_prompt to concept before returning

YOUR TASKS (static/js/studio.js):
  7. Write showImgLoading(), showImgResult(url), showImgError(msg)
  8. Write fetchImage(prompt) — POST to /generate-image, call
     showImgResult or showImgError based on response
  9. In runGeneration(): after concept loads, call fetchImage()

Run:  python app.py  →  http://localhost:5000/studio
"""

import os, json, base64, requests
from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = "sneaker-studio-dev-key"

GROQ_API_KEY        = os.environ.get("GROQ_API_KEY", "")
HCAPTCHA_SITE_KEY   = os.environ.get("HCAPTCHA_SITE_KEY", "10000000-ffff-ffff-ffff-000000000001")
HCAPTCHA_SECRET     = os.environ.get("HCAPTCHA_SECRET",   "0x0000000000000000000000000000000000000000")
HCAPTCHA_VERIFY_URL = "https://api.hcaptcha.com/siteverify"
groq_client         = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# ── TODO 1: Add HF_API_KEY and HF_IMAGE_URL ───────────────────


DESIGN_PROMPT = """You are an expert sneaker designer. Generate a detailed concept based on:
Style: {style}, Primary Color: {primary_color}, Accent Color: {accent_color},
Material: {material}, Occasion: {occasion}, Inspiration: {inspiration}

Respond with raw JSON only — no markdown, no explanation.
{{"name":"2-4 word creative name","tagline":"punchy tagline max 10 words","description":"2-3 sentence design description","materials":["mat1","mat2","mat3"],"colorways":[{{"name":"colorway name","sole":"#hex","upper":"#hex","accent":"#hex","lace":"#hex","tongue":"#hex"}}],"features":["feat1","feat2","feat3","feat4"],"sole_type":"sole tech description","target_audience":"who this is for","retail_price":"$XXX","style_tags":["tag1","tag2","tag3"]}}
Generate exactly 3 colorways: user colors first, then 2 creative variations. All hex codes must be valid #RRGGBB."""


def get_prefs(data):
    fields = [("style","casual"),("primary_color","white"),("accent_color","black"),
              ("material","leather"),("occasion","everyday"),("inspiration","")]
    return {k: data.get(k, d) for k, d in fields}


def verify_hcaptcha(token):
    try:
        r = requests.post(HCAPTCHA_VERIFY_URL,
                          data={"secret": HCAPTCHA_SECRET, "response": token}, timeout=5)
        return r.json().get("success", False)
    except Exception:
        return False


def generate_concept(prefs):
    if not groq_client: raise RuntimeError("GROQ_API_KEY not set.")
    chat = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"system","content":"Sneaker design expert. Pure JSON only."},
                  {"role":"user","content":DESIGN_PROMPT.format(**prefs)}],
        temperature=0.85, max_tokens=1200)
    raw = chat.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
    return json.loads(raw.strip().rstrip("```").strip())


# ── TODO 2: Write hex_to_color_name(h) ────────────────────────
# Parse r,g,b from hex → check brightness → check dominant channel
# Return a color name string like "black", "red", "blue", etc.


# ── TODO 3: Write generate_sneaker_image(prompt) ──────────────
# POST to HF_IMAGE_URL with Authorization header and {"inputs": prompt}
# If response is 200 and content-type starts with "image":
#   encode to base64 and return "data:{mime};base64,..."
# Return None on any failure


# ── TODO 4: Write build_image_prompt(prefs) ───────────────────
# Use hex_to_color_name() for primary and accent colors
# Build a descriptive prompt for FLUX, add inspiration if present


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/studio")
def studio():
    return render_template("studio.html", hcaptcha_site_key=HCAPTCHA_SITE_KEY)

@app.route("/history")
def history():
    return render_template("history.html", designs=[])


@app.route("/generate", methods=["POST"])
def generate():
    data  = request.get_json(silent=True) or request.form
    token = data.get("h-captcha-response", "")
    if not token:
        return jsonify({"error": "Please complete the CAPTCHA."}), 400
    if not verify_hcaptcha(token):
        return jsonify({"error": "CAPTCHA verification failed."}), 400
    prefs = get_prefs(data)
    try:
        concept = generate_concept(prefs)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Malformed AI response: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"Concept generation failed: {e}"}), 500

    # ── TODO 6: Attach image_prompt to concept ────────────────

    return jsonify({"success": True, "concept": concept, "prefs": prefs})


# ── TODO 5: Add /generate-image POST route ────────────────────
# Read image_prompt from body, validate, call generate_sneaker_image
# Return {"success": True, "image_url": ...} or error responses


if __name__ == "__main__":
    app.run(debug=True, port=5000)
