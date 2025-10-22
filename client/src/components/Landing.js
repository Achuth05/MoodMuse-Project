import { useState, useEffect } from "react";

const BASE_URL = "http://localhost:5000";

export function Landing({ onMoodSubmit, currentLanguage, userName, userEmail, userId }) {
  const [text, setText] = useState("");
  const [selectedMood, setSelectedMood] = useState("");
  const [selectedContentType, setSelectedContentType] = useState("movies");
  const [selectedLanguage, setSelectedLanguage] = useState(currentLanguage);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loadingActivity, setLoadingActivity] = useState(false);

  const moods = ["Happy / Joyful", "Sad / Melancholic", "Romantic / Love", "Energetic / Excited", "Calm / Relaxed"];
  const contentTypes = ["movies", "series"];
  const languages = [
    { code: "en", name: "English" },
    { code: "ml", name: "Malayalam" },
    { code: "hi", name: "Hindi" },
    { code: "ta", name: "Tamil" },
    { code: "te", name: "Telugu" },
    { code: "kn", name: "Kannada" },
  ];

  // Fetch recent activity on load / when userId changes
  useEffect(() => {
    const fetchActivity = async () => {
      if (!userId) return;
      
      try {
        setLoadingActivity(true);
        const res = await fetch(`${BASE_URL}/home/get_recent_activity?user_id=${encodeURIComponent(userId)}&limit=10`);
        const data = await res.json();
        
        if (res.ok) {
          const acts = data.activities || [];
          setRecentActivity(acts);
        } else {
          console.error("Failed to fetch recent activity:", data);
          setRecentActivity([]);
        }
      } catch (err) {
        console.error("Failed to fetch recent activity:", err);
        setRecentActivity([]);
      } finally {
        setLoadingActivity(false);
      }
    };
    
    fetchActivity();
  }, [userId]);

  const handleSubmit = async () => {
    if (!selectedMood && !text) {
      alert("Please select a mood or enter text describing your mood");
      return;
    }

    // Trigger recommendations in parent component
    onMoodSubmit(selectedMood, selectedContentType, selectedLanguage, text);

    // Log activity to backend using the /home/log_activity endpoint
    try {
      if (userId) {
        const resp = await fetch(`${BASE_URL}/home/log_activity`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_id: userId,
            action: `searched for ${selectedContentType}`,
            mood: selectedMood || text,
          }),
        });

        if (!resp.ok) {
          const err = await resp.json().catch(() => ({}));
          console.error("Log activity failed:", err);
        } else {
          // Optimistically prepend the new activity so it's visible immediately
          const body = await resp.json().catch(() => ({}));
          const newAct = body.activity || null;
          if (newAct) {
            setRecentActivity((prev) => [newAct, ...prev].slice(0, 10));
          }
        }
      }
    } catch (err) {
      console.error("Failed to log activity:", err);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen text-center p-6">
      <h1 className="text-4xl font-bold mb-6">🎭 MoodMuse</h1>

      {/* Recent activity */}
      {loadingActivity ? (
        <div className="p-4 mb-6 bg-yellow-100 rounded w-full max-w-md">Loading recent activity...</div>
      ) : recentActivity && recentActivity.length > 0 ? (
        <div className="p-4 mb-6 bg-yellow-100 rounded w-full max-w-md">
          <h3 className="font-semibold mb-2">📜 Recent Activity:</h3>
          <ul className="list-disc list-inside text-left">
            {recentActivity.map((act, idx) => (
              <li key={act.log_id || act.id || idx} className="mb-1">
                <span className="text-sm text-gray-700">{act.action}</span>
                <span className="font-medium ml-2">({act.mood})</span>
                {act.created_at && (
                  <span className="text-xs text-gray-500 ml-2">
                    {new Date(act.created_at).toLocaleString()}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <textarea
        placeholder="Describe your mood..."
        className="border p-2 rounded w-full max-w-md mb-4"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <div className="flex flex-wrap justify-center gap-3 mb-4">
        {moods.map((mood) => (
          <button
            key={mood}
            className={`px-4 py-2 rounded-xl ${
              selectedMood === mood ? "bg-green-500 text-white" : "bg-blue-500 text-white"
            }`}
            onClick={() => setSelectedMood(mood)}
          >
            {mood}
          </button>
        ))}
      </div>

      <div className="mb-4">
        <label className="mr-2 font-medium">Content Type:</label>
        <select
          value={selectedContentType}
          onChange={(e) => setSelectedContentType(e.target.value)}
          className="border p-2 rounded"
        >
          {contentTypes.map((ct) => (
            <option key={ct} value={ct}>
              {ct.charAt(0).toUpperCase() + ct.slice(1)}
            </option>
          ))}
        </select>
      </div>

      <div className="mb-4">
        <label className="mr-2 font-medium">Language:</label>
        <select
          value={selectedLanguage}
          onChange={(e) => setSelectedLanguage(e.target.value)}
          className="border p-2 rounded"
        >
          {languages.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
        </select>
      </div>

      <button
        onClick={handleSubmit}
        className="bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700"
      >
        Get Recommendations
      </button>
    </div>
  );
}
