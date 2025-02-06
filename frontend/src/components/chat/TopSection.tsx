import { useTheme } from "../../context/ThemeContext";
import ThemeToggle from "../ThemeToggle";
import { useSidebarContext } from "../../context/SideBarContext";
import ToggleIcon from "../../assets/icons/toggle-button.svg";
const TopSection = () => {
  const { theme, currentTheme } = useTheme();
  const { sideBarVisible, toggleSidebar } = useSidebarContext();

  return (
    <div
      className={`flex items-center px-6 py-1.5 transition-all z-40 ${
        sideBarVisible ? "justify-end" : "justify-between"
      }`}
      style={{
        backgroundColor: currentTheme.chatWindowBg,
        borderColor: currentTheme.secondaryFont,
      }}
    >
      {!sideBarVisible && (
        <button
          className="p-2 cursor-pointer "
          style={{ color: currentTheme.primaryFont }}
          onClick={toggleSidebar}
        >
          {/* <FiMenu /> */}
          {theme === "dark" ? (
            <img
              src={ToggleIcon}
              alt=""
              className={`opacity-60 hover:opacity-100 `}
            />
          ) : (
            <img
              src={ToggleIcon}
              alt=""
              className="invert opacity-60 hover:opacity-100"
            />
          )}
        </button>
      )}
      <div className="flex items-center gap-4">
        <ThemeToggle />

        <div
          className="w-8 h-8 rounded-full "
          style={{ backgroundColor: currentTheme.sideMenuBg }}
        ></div>
      </div>
    </div>
  );
};

export default TopSection;
