import { useState } from "react";

export function AuthModel({ isOpen, onClose, onLogin, onRegister }) {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ name: "", email: "", password: "" });

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isLogin) onLogin(formData.email, formData.password);
    else onRegister(formData.name, formData.email, formData.password);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex flex-col justify-center items-center z-50">
      <h1 className="text-3xl font-bold mb-4">🎭 MoodMuse</h1>
      <div className="bg-white p-6 rounded-2xl w-80 shadow-lg">
        <h2 className="text-xl font-semibold mb-4">{isLogin ? "Login" : "Register"}</h2>
        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <input
              type="text"
              placeholder="Name"
              className="w-full mb-3 p-2 border rounded"
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          )}
          <input
            type="email"
            placeholder="Email"
            className="w-full mb-3 p-2 border rounded"
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            required
          />
          <input
            type="password"
            placeholder="Password"
            className="w-full mb-3 p-2 border rounded"
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            required
          />
          <button className="w-full bg-blue-600 text-white py-2 rounded mb-3 hover:bg-blue-700">
            {isLogin ? "Login" : "Register"}
          </button>
        </form>
        <button
          onClick={() => setIsLogin(!isLogin)}
          className="text-blue-500 text-sm underline mb-3"
        >
          {isLogin ? "Create an account" : "Have an account? Login"}
        </button>
        <button onClick={onClose} className="text-gray-600 text-sm underline">
          Close
        </button>
      </div>
    </div>
  );
}
