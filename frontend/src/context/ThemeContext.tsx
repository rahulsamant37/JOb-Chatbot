import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import { DarkTheme, LightTheme } from "../theme";

interface ThemeContextProps {
  theme: string;
  currentTheme: typeof DarkTheme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextProps | undefined>(undefined);

// use default system theme:
// const getSystemTheme = () => {
//   return window.matchMedia("(prefers-color-scheme: dark)").matches
//     ? "dark"
//     : "light";
// };

export const ThemeProvider = ({ children }: { children: ReactNode }) => {
  const [theme, setTheme] = useState(localStorage.getItem("theme") || "light");
  // const [theme, setTheme] = useState(getSystemTheme());
  const [currentTheme, setCurrentTheme] = useState(
    theme === "dark" ? DarkTheme : LightTheme
  );

  // useEffect(() => {
  //   if (theme === "dark") {
  //     document.documentElement.classList.add("dark");
  //   } else {
  //     document.documentElement.classList.add("light");
  //   }
  //   localStorage.setItem("theme", theme);
  // }, [theme]);

  useEffect(() => {
    // console.log("Theme changed to:", theme);
    document.documentElement.classList.remove("light", "dark");
    document.documentElement.classList.add(theme);
    localStorage.setItem("theme", theme);
    setCurrentTheme(theme === "dark" ? DarkTheme : LightTheme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  return (
    <ThemeContext.Provider value={{ theme, currentTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};
