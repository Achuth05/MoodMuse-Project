import { useState } from "react";

export function Landing({ onMoodSubmit, currentLanguage, userName }) {
  const [text, setText] = useState("");
  const [selectedMood, setSelectedMood] = useState("");
  const [selectedContentType, setSelectedContentType] = useState("movies");
  const [selectedLanguage, setSelectedLanguage] = useState(currentLanguage);

  const moods = ["Happy", "Sad", "Romantic", "Energetic", "Calm"];
  const contentTypes = ["movies", "songs", "series"];
  const languages = [
    { code: "en", name: "English" },
    { code: "ml", name: "Malayalam" },
    { code: "hi", name: "Hindi" },
    { code: "ta", name: "Tamil" },
    { code: "te", name: "Telugu" },
    { code: "kn", name: "Kannada" },
  ];

  const handleSubmit = () => {
    if (!selectedMood && !text) {
      alert("Please select a mood or enter text describing your mood");
      return;
    }
    onMoodSubmit(selectedMood, selectedContentType, selectedLanguage, text);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen text-center p-6">
      <h1 className="text-4xl font-bold mb-6">🎵 MoodMuse</h1>

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
