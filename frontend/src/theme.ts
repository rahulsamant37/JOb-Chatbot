// Dark Mode:
export const DarkTheme = {
  primaryFont: "#FFFFFF",
  secondaryFont: "#BABABA",
  sideMenuBg: "#2B2D31",
  chatWindowBg: "#313338",
  chatInputBg: "#383A40",
  userMessageBg: "#2B2D31",
  jobCardBg: "#2B2D31",
  applyButton: "#3AAB63",
  sendButton: "#BABABA",
  agentMessageBg: "transparent", // Transparent background
};

// Light Mode:
export const LightTheme = {
  primaryFont: "#1A1A1A",
  secondaryFont: "#696969",
  sideMenuBg: "#F2F3F5",
  chatWindowBg: "#FFFFFF", //
  chatInputBg: "#FFFFFF",
  userMessageBg: "#F2F3F5",
  jobCardBg: "#F2F3F5",
  applyButton: "#3AAB63",
  sendButton: "#696969",
  agentMessageBg: "transparent", // Transparent background
};

// More themes for future...
// export const themeName = {};

// cur theme
export const getTheme = (theme: string) =>
  theme === "dark" ? DarkTheme : LightTheme;
