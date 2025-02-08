import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import BGImage from "../assets/images/LandingPage.png";
import { useState, useEffect } from "react";

const LandingPage = () => {
  const navigate = useNavigate();

  // const handleExecution = () => {
  //   const isLoggedIn = localStorage.getItem("user");
  //   if (isLoggedIn) {
  //     navigate("/chat");
  //   } else {
  //     navigate("/signup");
  //   }
  // };

  // BG Image Temporary...
  const getBgImage = () => (window.innerWidth >= 1024 ? `url(${BGImage})` : "none");
  const [bgImage, setBgImage] = useState(getBgImage());

  useEffect(() => {
    const handleResize = () => {
      setBgImage(getBgImage());
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return (
    <div
      style={{
        backgroundImage: bgImage,
        backgroundSize: "contain",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        // display: "none",
      }} // Replace with actual image path
      className="min-h-screen bg-cover bg-center flex flex-col items-center justify-center text-center px-6 md:bg-none"
    >
      <Navbar />

      {/* Company Name */}
      <h1 className="text-6xl font-bold text-black mb-6">XZAYOGN</h1>

      {/* Start to Execute Button */}
      {/* <Link to="/login">
        <button className="bg-blue-600 text-white px-6 py-3 rounded-xl text-lg font-semibold hover:bg-blue-700 transition">
          Start to Execute →
        </button>
      </Link> */}
      <button
        onClick={() => navigate("/chat")}
        className="bg-blue-600 text-white px-6 py-3 rounded-xl text-lg font-semibold hover:bg-blue-700 transition cursor-pointer"
      >
        Let's Start →
      </button>
    </div>
  );
};

export default LandingPage;
