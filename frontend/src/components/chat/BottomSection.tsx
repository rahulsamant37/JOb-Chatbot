import { useTheme } from "../../context/ThemeContext";

const BottomSection = () => {
  const { currentTheme } = useTheme();

  return (
    <div
      className="p-2 text-center text-sm"
      style={{
        backgroundColor: currentTheme.chatWindowBg,
        color: currentTheme.secondaryFont,
      }}
    >
      <p className="text-xs" style={{ color: currentTheme.secondaryFont }}>
        {/* FAQ • Privacy Policy • Terms of Service • Contact Us */}
      </p>
    </div>
  );
};

export default BottomSection;
