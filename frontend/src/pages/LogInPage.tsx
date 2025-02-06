import AuthPage from "../components/auth/AuthPage";

const LogInPage = () => {
  return <AuthPage mode="login" />;
};

export default LogInPage;

// import { useState } from "react";
// import { useNavigate } from "react-router-dom";
// import BGImage from "../assets/images/LoginBG.png";

// const LogInPage = () => {
//   const navigate = useNavigate();
//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");

//   // using local storage as of now!!!! use authentication methods here..
//   const handleLogIn = () => {
//     if (email && password) {
//       localStorage.setItem("user", JSON.stringify({ email }));
//       navigate("/chat");
//     }
//   };

//   return (
//     <div className="min-h-screen flex  bg-white">
//       <div className="hidden md:flex w-1/2 h-screen flex-col-reverse relative">
//         <img
//           src={BGImage}
//           alt=""
//           className="h-[calc(100vh-5rem)]  overflow-visible"
//         />
//       </div>
//       <div className="w-full md:w-1/2 flex justify-center items-center px-6">
//         <div className="bg-white rounded-lg p-8 max-w-lg w-full">
//           {/* Header */}
//           <h2 className="text-3xl font-bold text-center">Welcome back</h2>
//           <p className="text-center text-gray-500">
//             Create an account to get started.
//           </p>

//           {/* Log-In Form */}
//           <div className="mt-6 space-y-4">
//             <input
//               type="email"
//               placeholder="Email address"
//               value={email}
//               onChange={(e) => setEmail(e.target.value)}
//               className="w-full p-3 rounded-lg bg-gray-100"
//             />
//             <input
//               type="password"
//               placeholder="Password"
//               value={password}
//               onChange={(e) => setPassword(e.target.value)}
//               className="w-full p-3 rounded-lg bg-gray-100"
//             />

//             <button
//               onClick={handleLogIn}
//               className="w-full bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 transition"
//             >
//               Log In
//             </button>
//           </div>

//           {/* Alternative Sign-In */}
//           <p className="text-center mt-4">
//             Don't have an account?
//             <span
//               onClick={() => navigate("/signup")}
//               className="text-blue-600 cursor-pointer hover:underline"
//             >
//               Sign Up
//             </span>
//           </p>

//           <div className="mt-6 mb-6 text-center text-gray-500">OR</div>

//           <button className="w-full flex justify-center items-center bg-gray-50 border-2 border-gray-200 p-3 rounded-lg hover:bg-gray-100 transition">
//             <img src="/google-icon.png" alt="Google" className="w-6 h-6 mr-2" />
//             Log In with Google
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default LogInPage;
