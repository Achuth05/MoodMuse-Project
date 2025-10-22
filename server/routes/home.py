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
        # If the client sent an email as user_id, also include user_email column when inserting.
        # Supabase will ignore unknown columns if they don't exist in the table schema.
        insert_payload = {
            "user_id": user_id,
            "action": action,
            "mood": mood,
        }
        if isinstance(user_id, str) and "@" in user_id:
            insert_payload["user_email"] = user_id

        resp = sb.table("activity_logs").insert(insert_payload).execute()

        # Return the inserted row so frontend can confirm
        inserted = resp.data[0] if getattr(resp, "data", None) else None
        return jsonify({"status": "success", "activity": inserted})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

        # Order by created_at descending (most recent first)
        # Try matching `user_id` first; if that returns no rows, try `user_email`.
        resp = (
            sb.table("activity_logs")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        activities = resp.data or []

        if not activities:
            # try user_email column as a fallback (some clients send email as identifier)
            try:
                resp2 = (
                    sb.table("activity_logs")
                    .select("*")
                    .eq("user_email", user_id)
                    .order("created_at", desc=True)
                    .limit(limit)
                    .execute()
                )
                activities = resp2.data or []
            except Exception:
                # if fallback fails, keep activities as empty list
                activities = activities

        return jsonify({"activities": activities})
        return jsonify({"activities": []})

    try:
        # Order by created_at descending (most recent first)
        resp = (
            sb.table("activity_logs")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
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
            # Fallback: case-insensitive partial match
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

        results = query.range(offset, offset + limit - 1).execute()
        data_list = results.data or []
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Log the search activity - this will automatically record to activity_logs
    user_id = data.get("user_id")
    if user_id:
        try:
            sb.table("activity_logs").insert({
                "user_id": user_id,
                "action": f"searched for {content_type}",
                "mood": mood_name,
            }).execute()
        except Exception:
            # Don't fail the whole request if logging fails
            pass

    return jsonify({
        "mood": mood_name,
        "count": len(data_list),
        "results": data_list
    })