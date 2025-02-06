import { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import BGImage from "../../assets/images/LoginBG.png";
import { AuthContext } from "../../context/AuthContext";

interface AuthPageProps {
  mode: "login" | "signup";
}

const AuthPage = ({ mode }: AuthPageProps) => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // todo
  // const { login } = useContext(AuthContext);
  // const [error, setError] = useState("");

  //! Have to save JWT Token and update auth state here -> AuthContext
  //* Have to redirect to login page after successful signup
  //* Already created context/AuthContext.tsx
  //-------------------------------------------
  // Handle Login or Sign-up
  const handleAuth = () => {
    if (email && password) {
      // localStorage.setItem("user", JSON.stringify({ email }));
      //

      navigate("/chat");
    }
  };

  // Dynamic text based on mode
  const isLogin = mode === "login";

  return (
    <div className="min-h-screen flex bg-white">
      {/* Left-side image (only visible on medium+ screens) */}
      <div className="hidden md:flex w-1/2 h-screen flex-col-reverse relative">
        <img
          src={BGImage}
          alt="Auth Background"
          className="h-[calc(100vh-5rem)] overflow-visible"
        />
      </div>

      {/* Auth Form Section */}
      <div className="w-full md:w-1/2 flex justify-center items-center px-6">
        <div className="bg-white rounded-lg p-8 max-w-lg w-full">
          {/* Header */}
          <h2 className="text-3xl font-bold text-center">
            {isLogin ? "Welcome back" : "Join Us Today!"}
          </h2>
          <p className="text-center text-gray-500">
            {isLogin
              ? "Sign in to continue."
              : "Create an account to get started."}
          </p>

          {/* Auth Form */}
          <div className="mt-6 space-y-4">
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-3 rounded-lg bg-gray-100"
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-3 rounded-lg bg-gray-100"
            />

            <button
              onClick={handleAuth}
              className="w-full bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 transition"
            >
              {isLogin ? "Log In" : "Sign Up"}
            </button>
          </div>

          {/* Switch Between Login & Sign-Up */}
          <p className="text-center mt-4">
            {isLogin ? "Don't have an account?" : "Already have an account?"}
            <span
              onClick={() => navigate(isLogin ? "/signup" : "/login")}
              className="text-blue-600 cursor-pointer hover:underline ml-1"
            >
              {isLogin ? "Sign Up" : "Log In"}
            </span>
          </p>

          {/* Alternative Sign-In */}
          <div className="mt-6 mb-6 text-center text-gray-500">OR</div>

          <button className="w-full flex justify-center items-center bg-gray-50 border-2 border-gray-200 p-3 rounded-lg hover:bg-gray-100 transition">
            <img src="/google-icon.png" alt="Google" className="w-6 h-6 mr-2" />
            {isLogin ? "Log In" : "Sign Up"} with Google
          </button>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
