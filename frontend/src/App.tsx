import "./App.css";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import { ThemeProvider } from "./context/ThemeContext";
import Layout from "./components/Layout";

import LandingPage from "./pages/LandingPage";
import FeaturesPage from "./pages/FeaturesPage";
import PricingPage from "./pages/PricingPage";

import SignUpPage from "./pages/SignUpPage";
import LogInPage from "./pages/LogInPage";

import ChatUI from "./pages/ChatUI";

function App() {
  return (
    <ThemeProvider>
      <Router>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<LandingPage />} />
            <Route path="/signup" element={<SignUpPage />} />
            <Route path="/login" element={<LogInPage />} />
            <Route path="/features" element={<FeaturesPage />} />
            <Route path="/pricing" element={<PricingPage />} />
          </Route>
          <Route path="/chat" element={<ChatUI />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
