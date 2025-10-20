import { useEffect, useState } from "react";
import { toast } from "sonner";

const BASE_URL = "http://localhost:5000";

export function Recommendations({ mood, text, contentType, language, onBack, userName }) {
  const [recommendations, setRecommendations] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const limit = 20;

  const fetchRecommendations = async (pageNum = 1) => {
    try {
      const res = await fetch(`${BASE_URL}/home/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mood, text, content_type: contentType, language, page: pageNum, limit }),
      });
      const data = await res.json();
      console.log("Fetched recommendations:", data);

      if (res.ok) {
        if (pageNum === 1) setRecommendations(data.results || []);
        else setRecommendations((prev) => [...prev, ...(data.results || [])]);
        setHasMore((data.results || []).length === limit);
      } else {
        console.error("Recommendations request failed:", data);
        toast.error(data.error || "No recommendations available");
        setRecommendations([]);
      }
    } catch {
      toast.error("Failed to fetch recommendations. Check your connection or server.");
      setRecommendations([]);
    }
  };

  useEffect(() => {
    setPage(1);
    fetchRecommendations(1);
  }, [mood, contentType, language]);

  const loadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchRecommendations(nextPage);
  };

  return (
    <div className="p-6">
      <button onClick={onBack} className="text-blue-600 underline mb-4">
        ← Back
      </button>

      <h2 className="text-2xl font-bold mb-4">
        {userName ? `${userName}'s ` : ""}{mood} {contentType.charAt(0).toUpperCase() + contentType.slice(1)} Recommendations
      </h2>

      <ul className="space-y-3">
        {recommendations.length > 0 ? (
          recommendations.map((item, i) => (
            <li key={i} className="border p-3 rounded-xl bg-gray-50">{item.title}</li>
          ))
        ) : (
          <p>No recommendations found</p>
        )}
      </ul>

      {hasMore && (
        <button
          onClick={loadMore}
          className="mt-6 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Load More
        </button>
      )}
    </div>
  );
}