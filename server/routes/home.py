from flask import Blueprint, request, jsonify
from utils.sup_client import sb
from utils.mood_extract import extract_mood

home_bp = Blueprint("home", __name__)

@home_bp.route("/log_activity", methods=["POST"])
def log_activity():
    data = request.get_json()
    user_id = data.get("user_id")
    action = data.get("action")  # e.g., "searched for movies"
    mood = data.get("mood")      # e.g., "Sad"
    
    if not user_id or not action:
        return jsonify({"error": "Missing user_id or action"}), 400

    try:
        resp = sb.table("activity_logs").insert({
            "user_id": user_id,
            "action": action,
            "mood": mood
        }).execute()

        # return the inserted row when possible so frontend can confirm
        inserted = resp.data[0] if getattr(resp, "data", None) else None
        return jsonify({"status": "success", "activity": inserted})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@home_bp.route("/get_recent_activity", methods=["GET"])
def get_recent_activity():
    """Return recent activity rows for a user. Query params: user_id (required), limit (optional)"""
    user_id = request.args.get("user_id")
    try:
        limit = int(request.args.get("limit", 10))
    except Exception:
        limit = 10

    if not user_id:
        return jsonify({"activities": []})

    try:
        # Try ordering by created_at first; if that column doesn't exist, fall back to log_id
        try:
            resp = (
                sb.table("activity_logs")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .range(0, limit - 1)
                .execute()
            )
        except Exception:
            resp = (
                sb.table("activity_logs")
                .select("*")
                .eq("user_id", user_id)
                .order("log_id", desc=True)
                .range(0, limit - 1)
                .execute()
            )

        activities = resp.data or []
        return jsonify({"activities": activities})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

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

    # Optionally log the search as activity if user_id provided in the request
    user_id = data.get("user_id")
    if user_id:
        try:
            sb.table("activity_logs").insert({
                "user_id": user_id,
                "action": f"searched for {content_type}",
                "mood": mood_name,
            }).execute()
        except Exception:
            # don't fail the whole request if logging fails
            pass

    return jsonify({
        "mood": mood_name,
        "count": len(data_list),
        "results": data_list
    })

