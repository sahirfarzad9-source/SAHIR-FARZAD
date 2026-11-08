"""
╔══════════════════════════════════════════════════════════════╗
║  LESSON 6 — Managing History and Finalizing the Studio       ║
╚══════════════════════════════════════════════════════════════╝

GOAL: Persist every generated design to the Flask session so
      the History page shows all past concepts with images
      and colorway swatches.

YOUR TASKS (app.py):
  1. Add session, redirect, url_for to Flask imports
     Add uuid and datetime imports
  2. Write save_to_history(concept, prefs, image_url=None)
  3. Update /history route to read from session["history"]
  4. Add /clear-history POST route
  5. In /generate: call save_to_history(), return history_id
  6. In /generate-image: patch entry by history_id in session

YOUR TASKS (static/js/studio.js):
  7. Add currentHistoryId variable
  8. Update fetchImage() to send history_id in request body
  9. In runGeneration(): store d.history_id in currentHistoryId
  10. Wire "New Concept" button to reset currentHistoryId

Run:  python app.py  ->  generate concepts, visit /history
"""

import os, json, base64, requests
from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "sneaker-studio-dev-key")

GROQ_API_KEY        = os.environ.get("GROQ_API_KEY", "")
HF_API_KEY          = os.environ.get("HF_API_KEY", "")
HCAPTCHA_SITE_KEY   = os.environ.get("HCAPTCHA_SITE_KEY", "10000000-ffff-ffff-ffff-000000000001")
HCAPTCHA_SECRET     = os.environ.get("HCAPTCHA_SECRET",   "0x0000000000000000000000000000000000000000")
HCAPTCHA_VERIFY_URL = "https://api.hcaptcha.com/siteverify"
HF_IMAGE_URL        = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
groq_client         = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# TODO 1: Add session, redirect, url_for to Flask imports above
#         Also add: import uuid  and  from datetime import datetime


DESIGN_PROMPT = """You are an expert sneaker designer. Generate a detailed concept based on:
Style: {style}, Primary Color: {primary_color}, Accent Color: {accent_color},
Material: {material}, Occasion: {occasion}, Inspiration: {inspiration}

Respond with raw JSON only -- no markdown, no explanation.
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


def hex_to_color_name(h):
    h = h.lstrip("#").lower()
    try: r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    except: return h
    mx, mn = max(r,g,b), min(r,g,b)
    br, sat = mx/255, (mx-mn)/mx if mx else 0
    if br < 0.15: return "black"
    if br > 0.88 and sat < 0.15: return "white"
    if sat < 0.18: return "dark gray" if br < 0.4 else "gray" if br < 0.65 else "light gray"
    if mx == r: return ("orange" if g > 120 else "dark orange") if g > b+60 else "magenta" if b > g+40 else "red"
    if mx == g: return "yellow-green" if r > b+60 else "cyan-green" if b > r+40 else "green"
    if mx == b: return "purple" if r > g+60 else "cyan" if g > r+40 else "blue"
    return "colorful"


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


def generate_sneaker_image(prompt):
    if not HF_API_KEY: return None
    try:
        r = requests.post(HF_IMAGE_URL,
            headers={"Authorization": f"Bearer {HF_API_KEY}", "Content-Type": "application/json"},
            json={"inputs": prompt}, timeout=60)
        if r.status_code == 200 and r.headers.get("content-type","").startswith("image"):
            mime = r.headers["content-type"].split(";")[0].strip()
            return f"data:{mime};base64,{base64.b64encode(r.content).decode()}"
    except Exception:
        pass
    return None


def build_image_prompt(prefs):
    p = hex_to_color_name(prefs["primary_color"])
    a = hex_to_color_name(prefs["accent_color"])
    prompt = (f"Professional product photography of a {prefs['style']} sneaker, "
              f"{p} {prefs['material']} upper, {a} accent, {a} heel, white sole, "
              f"side view, white background, sharp focus, 8k, shoe only")
    if prefs.get("inspiration"):
        prompt += f", {prefs['inspiration']} theme"
    return prompt


# TODO 2: Write save_to_history(concept, prefs, image_url=None)
#   - session.setdefault("history", [])
#   - create entry dict with id (uuid[:8]), timestamp, concept, prefs, image_url
#   - prepend to session["history"], keep last 20


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/studio")
def studio():
    return render_template("studio.html", hcaptcha_site_key=HCAPTCHA_SITE_KEY)


# TODO 3: Update /history to read from session["history"]
@app.route("/history")
def history():
    designs = []  # replace: designs = session.get("history", [])
    return render_template("history.html", designs=designs)


# TODO 4: Add /clear-history POST route
#   - session.pop("history", None)
#   - return redirect(url_for("history"))


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
    concept["image_prompt"] = build_image_prompt(prefs)

    # TODO 5: Call save_to_history(concept, prefs)
    #         Get history_id = session["history"][0]["id"]
    #         Return it: jsonify({..., "history_id": history_id})

    return jsonify({"success": True, "concept": concept, "prefs": prefs})


@app.route("/generate-image", methods=["POST"])
def generate_image():
    data       = request.get_json(silent=True) or {}
    prompt     = data.get("image_prompt", "")
    history_id = data.get("history_id", "")
    if not prompt:
        return jsonify({"error": "No image prompt."}), 400
    if not HF_API_KEY:
        return jsonify({"error": "HF_API_KEY not configured."}), 503
    image_url = generate_sneaker_image(prompt)
    if not image_url:
        return jsonify({"error": "Image generation failed. Try again."}), 500

    # TODO 6: Find entry by history_id in session["history"]
    #         Set entry["image_url"] = image_url
    #         Set session.modified = True

    return jsonify({"success": True, "image_url": image_url})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
