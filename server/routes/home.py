from flask import Blueprint, request, jsonify
from app.services.supabase_client import sb
from utils.mood_extract import extract_mood

bp = Blueprint("home", __name__)

@bp.route("/home", methods=["POST"])
def recommend_content():
    data = request.get_json()
    mood_name = data.get("mood")
    text = data.get("text") 
    content_type = data.get("content_type", "movies") 
    language = data.get("language")

    
    if text and not mood_name:
        mood_name = extract_mood(user_text)

    if not mood_name:
        return jsonify({"error": "Mood not recognized"}), 400

    mood_resp = sb.table("moods").select("mood_id").eq("mood_name", mood_name).execute()
    if not mood_resp.data:
        return jsonify({"error": "Mood not found in DB"}), 404
    mood_id = mood_resp.data[0]["mood_id"]

    query = sb.table(content_type).select("*").eq("mood_id", mood_id)
    if language:
        query = query.eq("language", language)

    results = query.limit(20).execute()

    return jsonify({
        "mood": mood_name,
        "count": len(results.data),
        "results": results.data
    })
