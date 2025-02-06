import { useTheme } from "../context/ThemeContext";
import TopSection from "../components/chat/TopSection";
import MiddleSection from "../components/chat/MiddleSection";
import BottomSection from "../components/chat/BottomSection";
import SideBar from "../components/chat/SideBar";
import { useSidebarContext, SidebarProvider } from "../context/SideBarContext";

const ChatLayout = () => {
  const { sideBarVisible, toggleSidebar } = useSidebarContext();

  return (
    <div className="flex h-screen relative">
      <SideBar />

      {sideBarVisible && (
        <div
          className="fixed inset-0 bg-black opacity-50 md:hidden z-50"
          onClick={toggleSidebar}
        ></div>
      )}

      <div className="flex flex-col flex-1">
        <TopSection />
        <MiddleSection />
        <BottomSection />
      </div>
    </div>
  );
};

const ChatUI = () => {
  return (
    <SidebarProvider>
      <ChatLayout />
    </SidebarProvider>
  );
};

export default ChatUI;

// New ChatUI:

// SideBar
// SideBarContext
// MiddleSection
// TopSection
// BottomSection

{
  /* <SidebarProvider>
<div className="flex h-screen">
  <SideBar />
  <div className="flex flex-col flex-1">
    <TopSection />

    <MiddleSection />

    <BottomSection />
  </div>
</div>
</SidebarProvider> */
}
