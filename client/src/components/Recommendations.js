import { useEffect, useState } from "react";
import { toast } from "sonner";

const BASE_URL = "http://localhost:5000";

export function Recommendations({ mood, text, contentType, language, onBack, userName, userEmail }) {
  const [recommendations, setRecommendations] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const limit = 20;

  const fetchRecommendations = async (pageNum = 1) => {
    try {
      const res = await fetch(`${BASE_URL}/home/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mood, text, content_type: contentType, language, page: pageNum, limit, user_id: userEmail }),
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
          recommendations.map((item, i) => {
            const key = item.api_id || item.id || item.title || i;
            const title = item.title || item.name || item.track_name || "Untitled";
            const artist = item.artist || item.artists || item.performer || item.director;
            const genre = item.genre || item.genres || (item.genre_names && item.genre_names.join(", "));
            const year = item.release_year || item.year || item.first_air_date || item.release_date;
            const desc = item.description || item.overview || item.summary || item.plot;

            return (
              <li key={key} className="border p-3 rounded-xl bg-gray-50">
                <div className="flex items-start gap-4">
                  {/* Poster / thumbnail if available */}
                  {item.poster_path || item.image || item.thumbnail ? (
                    <img
                      src={item.poster_path || item.image || item.thumbnail}
                      alt={title}
                      className="w-20 h-28 object-cover rounded"
                    />
                  ) : null}

                  <div className="flex-1 text-left">
                    <div className="flex items-baseline justify-between">
                      <h3 className="font-semibold text-lg">{title}</h3>
                      {year && <span className="text-sm text-gray-500 ml-2">{String(year).slice(0,4)}</span>}
                    </div>

                    {artist && <div className="text-sm text-gray-700">{Array.isArray(artist) ? artist.join(", ") : artist}</div>}
                    {genre && <div className="text-sm text-gray-500">{genre}</div>}

                    {desc && <p className="mt-2 text-sm text-gray-700">{desc}</p>}

                    {/* Song-specific audio features */}
                    {contentType === "songs" && (item.valence !== undefined || item.energy !== undefined || item.tempo !== undefined) && (
                      <div className="mt-2 text-sm text-gray-600">
                        {item.valence !== undefined && <span className="mr-3">Valence: {Number(item.valence).toFixed(2)}</span>}
                        {item.energy !== undefined && <span className="mr-3">Energy: {Number(item.energy).toFixed(2)}</span>}
                        {item.tempo !== undefined && <span>Tempo: {Math.round(item.tempo)}</span>}
                      </div>
                    )}

                    {/* External links (Spotify etc.) */}
                    <div className="mt-3 flex gap-3 items-center">
                      {item.spotify_id && (
                        <a
                          className="text-sm text-green-600 hover:underline"
                          href={`https://open.spotify.com/track/${item.spotify_id}`}
                          target="_blank"
                          rel="noreferrer"
                        >
                          Open on Spotify
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              </li>
            );
          })
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