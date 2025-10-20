export function Navbar({ userName, onProfile, onLogout }) {
  return (
    <div className="flex justify-between items-center p-4 bg-gray-800 text-white">
      <h1 className="font-bold text-xl">MoodMuse</h1>
      <div className="flex items-center space-x-4">
        {userName && <span>Hi, {userName}</span>}
        <button
          onClick={onProfile}
          className="bg-blue-600 px-3 py-1 rounded hover:bg-blue-700"
        >
          Profile
        </button>
        <button
          onClick={onLogout}
          className="bg-red-600 px-3 py-1 rounded hover:bg-red-700"
        >
          Logout
        </button>
      </div>
    </div>
  );
}