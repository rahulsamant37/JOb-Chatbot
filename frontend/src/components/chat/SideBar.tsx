import { useSidebarContext } from "../../context/SideBarContext";
import { useTheme } from "../../context/ThemeContext";
import { useNavigate } from "react-router-dom";

import { FaPlus } from "react-icons/fa";
import { MdOutlineHistory } from "react-icons/md";
import ToggleIcon from "../../assets/icons/toggle-button.svg";
import UpcomingIcon from "../../assets/icons/upcoming-icon-sidemenu.svg";

const SideBar = () => {
  const { sideBarVisible, toggleSidebar } = useSidebarContext();
  const { theme, currentTheme } = useTheme();

  // upcoming features navigation
  const navigate = useNavigate();
  const handleNavigation = () => {
    navigate("/features");
  };

  return (
    <div
      className={`transition-all duration-300 overflow-hidden h-full flex flex-col
                    ${sideBarVisible ? "w-64 px-3 py-2" : "w-0"} 
                    ${
                      sideBarVisible
                        ? "fixed top-0 left-0 z-60 md:relative "
                        : ""
                    }
                    `}
      style={{ backgroundColor: currentTheme.sideMenuBg }}
    >
      <div className={`flex justify-between items-center `}>
        <div
          className="text-xl font-bold"
          style={{ color: currentTheme.primaryFont }}
        >
          {sideBarVisible ? "XZAYOGN" : ""}
        </div>
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
              className="opacity-60 hover:opacity-100"
            />
          ) : (
            <img
              src={ToggleIcon}
              alt=""
              className="invert opacity-60 hover:opacity-100"
            />
          )}
        </button>
      </div>

      {/* Sidebar Links */}
      {!sideBarVisible && (
        <div
          className="space-y-2 w-full p-2.5 px-4 my-4"
          style={{ color: currentTheme.primaryFont }}
        >
          {/* <FaPlus /> */}
          {/* Add quick access features here */}
        </div>
      )}
      <div
        className={`p-2 space-y-2 ${
          sideBarVisible ? "opacity-100" : "hidden"
        } transition-opacity`}
      >
        <button
          onClick={handleNavigation}
          className="w-full p-2.5 px-4 my-4 text-left text-s  rounded-xl flex justify-between items-center cursor-pointer hover:inset-ring"
          style={{
            backgroundColor: currentTheme.chatInputBg,
            color: currentTheme.primaryFont,
          }}
        >
          Upcoming
          <img src={UpcomingIcon} alt="" className="h-6 " />
        </button>

        <button
          className="w-full p-2.5 px-4 my-4 text-left text-s rounded-xl flex justify-between items-center cursor-pointer"
          style={{
            backgroundColor: currentTheme.chatInputBg,
            color: currentTheme.primaryFont,
          }}
        >
          New Chat
          <FaPlus />
        </button>
      </div>

      <div
        className={`p-2 space-y-2 ${
          sideBarVisible ? "opacity-100" : "hidden"
        } transition-opacity`}
      >
        <div className="mt-4">
          <p
            className="text-xs mb-2"
            style={{ color: currentTheme.secondaryFont }}
          >
            Quick Prompt:
          </p>
          <button
            className="w-full p-2.5 px-4 my-4 text-left text-s  rounded-xl flex justify-between items-center cursor-pointer"
            style={{
              backgroundColor: currentTheme.chatInputBg,
              color: currentTheme.primaryFont,
            }}
          >
            Find me a job...
          </button>
        </div>
      </div>
      <div
        className={`p-2 space-y-2 ${
          sideBarVisible ? "opacity-100" : "hidden"
        } transition-opacity`}
      >
        <div className="mt-4">
          <p
            className="text-xs mb-2 flex items-end"
            style={{ color: currentTheme.secondaryFont }}
          >
            Today
            <span className="mx-2 text-xs">
              <MdOutlineHistory />
            </span>
          </p>
          <button
            className="w-full p-2.5 px-4 my-4 text-left text-s  rounded-xl flex justify-between items-center cursor-pointer"
            style={{
              backgroundColor: currentTheme.chatInputBg,
              color: currentTheme.primaryFont,
            }}
          >
            Chat History...
          </button>
        </div>
      </div>
    </div>
  );
};

export default SideBar;

// <div
// className="p-3 border-t border-opacity-30"
// style={{ borderColor: currentTheme.primaryFont }}
// >
// <a
//   href="#"
//   className="flex items-center space-x-2 p-2 rounded-lg hover:bg-opacity-20"
//   style={{ color: currentTheme.primaryFont }}
// >
//   <span>⭐</span> {/* Upgrade Icon */}
//   <div>
//     <p className="text-sm font-medium">Upgrade Plan</p>
//     <p className="text-xs opacity-80">More access to the best models</p>
//   </div>
// </a>
// </div>
