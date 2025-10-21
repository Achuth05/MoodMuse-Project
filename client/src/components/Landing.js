import { useState, useEffect } from "react";

export function Landing({ onMoodSubmit, currentLanguage, userName, userEmail }) {
  const [text, setText] = useState("");
  const [selectedMood, setSelectedMood] = useState("");
  const [selectedContentType, setSelectedContentType] = useState("movies");
  const [selectedLanguage, setSelectedLanguage] = useState(currentLanguage);
  const [recentActivity, setRecentActivity] = useState([]);

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

  // Fetch recent activity on load
  useEffect(() => {
    const fetchActivity = async () => {
      try {
        const id = userEmail || userName;
        if (!id) return;
        const res = await fetch(`/get_recent_activity?user_id=${encodeURIComponent(id)}`);
        const data = await res.json();
        setRecentActivity(data.activities || []);
      } catch (err) {
        console.error("Failed to fetch recent activity:", err);
      }
    };
    fetchActivity();
  }, [userName, userEmail]);

  const handleSubmit = async () => {
    if (!selectedMood && !text) {
      alert("Please select a mood or enter text describing your mood");
      return;
    }

    // Trigger recommendations in parent component
    onMoodSubmit(selectedMood, selectedContentType, selectedLanguage, text);

    // Log activity to backend
    try {
      const id = userEmail || userName;
      if (id) {
        await fetch("/log_activity", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_id: id,
            action: `searched for ${selectedContentType}`,
            mood: selectedMood || text,
          }),
        });
      }
    } catch (err) {
      console.error("Failed to log activity:", err);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen text-center p-6">
      <h1 className="text-4xl font-bold mb-6"> MoodMuse</h1>

      {/* Recent activity */}
      {recentActivity.length > 0 && (
        <div className="p-4 mb-6 bg-yellow-100 rounded w-full max-w-md">
          <h3 className="font-semibold mb-2">Recent Activity:</h3>
          <ul className="list-disc list-inside text-left">
            {recentActivity.map((act) => (
              <li key={act.log_id}>
                {act.action} - <span className="font-medium">{act.mood}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

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
