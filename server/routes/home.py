from flask import Blueprint, request, jsonify
from utils.sup_client import sb
from utils.mood_extract import extract_mood

home_bp = Blueprint("home", __name__)

@home_bp.route("/", methods=["POST"])
def recommend_content():
    data = request.get_json()
    mood_name = data.get("mood")
    text = data.get("text") 
    content_type = data.get("content_type", "movies")
    language = data.get("language")
    page = int(data.get("page", 1))
    limit = int(data.get("limit", 20))
    offset = (page - 1) * limit

    # Extract mood if not provided
    if text and not mood_name:
        mood_name = extract_mood(text)

    if not mood_name:
        return jsonify({"error": "Mood not recognized"}), 400

    # Validate content_type
    if content_type not in ["movies", "songs", "series"]:
        return jsonify({"error": "Invalid content type"}), 400

    # Fetch mood_id from DB
    try:
        # Try exact match first
        mood_resp = sb.table("moods").select("mood_id, mood_name").eq("mood_name", mood_name).execute()
        if not mood_resp.data:
            # Fallback: case-insensitive partial match (ilike) so 'Happy' matches 'Happy / Joyful'
            mood_resp = sb.table("moods").select("mood_id, mood_name").ilike("mood_name", f"%{mood_name}%").execute()

        if not mood_resp.data:
            return jsonify({"error": "Mood not found in DB"}), 404

        mood_id = mood_resp.data[0]["mood_id"]
    except Exception as e:
        return jsonify({"error": "Database query failed: " + str(e)}), 400

    # Fetch content matching mood and language with pagination
    try:
        query = sb.table(content_type).select("*").eq("mood_id", mood_id)
        if language:
            query = query.eq("language", language)

        # Supabase uses range(offset, offset+limit-1) for pagination
        results = query.range(offset, offset + limit - 1).execute()
        data_list = results.data or []
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({
        "mood": mood_name,
        "count": len(data_list),
        "results": data_list
    })

