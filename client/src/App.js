import { useState } from "react";
import { Landing } from "./components/Landing";
import { AuthModel } from "./components/AuthModel";
import { Recommendations } from "./components/Recommendations";
import { UserProfile } from "./components/UserProfile";
import { Navbar } from "./components/Navbar";
import { Toaster } from "sonner";
import { toast } from "sonner";

const BASE_URL = "http://localhost:5000";

export default function App() {
  const [currentView, setCurrentView] = useState("auth"); 
  const [selectedMood, setSelectedMood] = useState("");
  const [selectedContentType, setSelectedContentType] = useState("movies");
  const [selectedLanguage, setSelectedLanguage] = useState("en");
  const [user, setUser] = useState({ 
    name: "User", 
    email: "", 
    userId: null,
    isAuthenticated: false 
  });
  const [showAuthModal, setShowAuthModal] = useState(true);
  const [enteredText, setEnteredText] = useState("");

  // Login handler
  const handleLogin = async (email, password) => {
    try {
      const res = await fetch(`${BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (res.ok) {
        setUser({
          name: data.user_metadata?.name || data.name || "User",
          email: data.user || email,
          // backend may not return a numeric user_id; fall back to email
          userId: data.user_id || data.user || email,
          isAuthenticated: true,
          accessToken: data.access_token,
        });
        toast.success(`Welcome back, ${data.user_metadata?.name || "User"}!`);
        setShowAuthModal(false);
        setCurrentView("landing");
      } else {
        toast.error(data.error || "Invalid credentials");
      }
    } catch {
      toast.error("Login failed. Try again later.");
    }
  };

  // Register handler
  const handleRegister = async (name, email, password) => {
    try {
      const res = await fetch(`${BASE_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      });
      const data = await res.json();
      if (res.ok) {
        setUser({
          name: name || "User",
          email: data.user || email,
          // backend may not return user_id; use returned email or provided email
          userId: data.user_id || data.user || email,
          isAuthenticated: true,
        });
        toast.success(`Welcome to MoodMuse, ${name || "User"}!`);
        setShowAuthModal(false);
        setCurrentView("landing");
      } else {
        toast.error(data.error || "Registration failed");
      }
    } catch {
      toast.error("Registration failed. Try again later.");
    }
  };

  // Logout handler
  const handleLogout = async () => {
    try {
      await fetch(`${BASE_URL}/auth/logout`, { method: "POST" });
      setUser({ name: "User", email: "", userId: null, isAuthenticated: false });
      setCurrentView("auth");
      setSelectedMood("");
      setShowAuthModal(true);
      toast.success("Logged out successfully");
    } catch {
      toast.error("Error logging out");
    }
  };

  // Mood submit from landing page
  const handleMoodSubmit = (mood, contentType, language, text) => {
    setEnteredText(text);
    setSelectedMood(mood);
    setSelectedContentType(contentType);
    setSelectedLanguage(language);
    setCurrentView("recommendations");
  };

  const handleBackToLanding = () => setCurrentView("landing");
  const handleBackFromProfile = () => setCurrentView("landing");

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar visible after login */}
      {user.isAuthenticated && (
        <Navbar
          userName={user.name}
          onProfile={() => setCurrentView("profile")}
          onLogout={handleLogout}
        />
      )}

      {/* Auth Page */}
      {currentView === "auth" && (
        <AuthModel
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          onLogin={handleLogin}
          onRegister={handleRegister}
        />
      )}

      {/* Landing Page */}
      {currentView === "landing" && (
        <Landing
          onMoodSubmit={handleMoodSubmit}
          currentLanguage={selectedLanguage}
          userName={user.name}
          userEmail={user.email}
          userId={user.userId}
        />
      )}

      {/* Recommendations Page */}
      {currentView === "recommendations" && (
        <Recommendations
          mood={selectedMood}
          text={enteredText}
          contentType={selectedContentType}
          language={selectedLanguage}
          onBack={handleBackToLanding}
          userName={user.name}
          userEmail={user.email}
          userId={user.userId}
        />
      )}

      {/* Profile Page */}
      {currentView === "profile" && (
        <UserProfile
          userName={user.name}
          userEmail={user.email}
          userId={user.userId}
          onBack={handleBackFromProfile}
          onLogout={handleLogout}
        />
      )}

      <Toaster position="top-right" />
    </div>
  );
}