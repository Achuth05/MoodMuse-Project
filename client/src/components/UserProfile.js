export function UserProfile({ userName, userEmail, onBack, onLogout }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen text-center">
      <h2 className="text-3xl font-semibold mb-4">👤 Profile</h2>
      <p className="text-lg mb-2">Name: {userName}</p>
      <p className="text-lg mb-6">Email: {userEmail}</p>

      <div className="space-x-3">
        <button onClick={onBack} className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400">
          Back
        </button>
        <button onClick={onLogout} className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">
          Logout
        </button>
      </div>
    </div>
  );
}

