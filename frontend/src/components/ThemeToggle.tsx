import { useTheme } from "../context/ThemeContext";

const ThemeToggle = () => {
  const { theme, toggleTheme, currentTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="p-1 px-1.5 rounded-full transition"
      style={{
        backgroundColor: currentTheme.sideMenuBg,
        color: currentTheme.primaryFont,
      }}
    >
      {theme === "light" ? "🌙" : "☀️"}
    </button>
  );
};

export default ThemeToggle;
