import { useState } from "react";
import { Link } from "react-router-dom";
import XLogo from "../assets/icons/xzayogn-logo.svg";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 w-full bg-white p-4 flex items-center justify-between px-12 z-50">
      {/* Left Side - Logo */}
      <Link to="/" className="flex items-center">
        <div className="w-12 h-12 rounded-full flex items-center justify-center">
          <img src={XLogo} alt="" className="text-white text-2xl font-bold" />
        </div>
      </Link>

      {/* Desktop Navigation */}
      <div className="hidden md:flex space-x-16 text-lg font-semibold">
        <Link to="/" className="hover:text-blue-500 transition">
          Home
        </Link>
        <Link to="/features" className="hover:text-blue-500 transition">
          Features
        </Link>
        <Link to="/pricing" className="hover:text-blue-500 transition">
          Pricing
        </Link>
      </div>

      {/* Mobile Menu Button (Hamburger) */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="md:hidden text-3xl focus:outline-none"
      >
        {isOpen ? "✖" : "☰"}
      </button>

      {/* Mobile Dropdown Menu */}
      <div
        className={`absolute top-16 right-0 w-full  md:hidden flex flex-col text-center py-4 transition-all duration-300 ease-in-out ${
          isOpen
            ? "opacity-100 translate-y-0 "
            : "opacity-0 -translate-y-4 pointer-events-none"
        }`}
      >
        <Link
          to="/"
          className="py-2 text-lg font-semibold hover:text-blue-500 transition"
          onClick={() => setIsOpen(false)}
        >
          Home
        </Link>
        <Link
          to="/features"
          className="py-2 text-lg font-semibold hover:text-blue-500 transition"
          onClick={() => setIsOpen(false)}
        >
          Features
        </Link>
        <Link
          to="/pricing"
          className="py-2 text-lg font-semibold hover:text-blue-500 transition"
          onClick={() => setIsOpen(false)}
        >
          Pricing
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;
