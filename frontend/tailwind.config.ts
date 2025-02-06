/** @type {import('tailwindcss').Config} */

export default {
  future: {},
  purge: [],
  variants: {},
  darkMode: "class", //enables clas using darkmode
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primaryFontDark: "#FFFFFF",
        secondaryFontDark: "#BABABA",
        sideMenuBgDark: "#2B2D31",
        chatWindowBgDark: "#313338",
        userMessageBgDark: "#2B2D31",
        jobCardBgDark: "#2B2D31",
        chatInputBgDark: "#383A40",
        sendButtonDark: "#BABABA",

        primaryFontLight: "#1A1A1A",
        secondaryFontLight: "#696969",
        sideMenuBgLight: "#F2F3F5",
        chatWindowBgLight: "#FFFFFF",
        userMessageBgLight: "#F2F3F5",
        jobCardBgLight: "#F2F3F5",
        chatInputBgLight: "#FFFFFF",
        applyButton: "#3AAB63",
        sendButtonLight: "#696969",
      },
      boxShadow: {
        chatInputLight: "0px 6px 9px rgba(0, 0, 0, 0.06)",
      },
      borderColor: {
        chatInputStroke: "#D1D1D1",
      },
    },
  },
  plugins: [],
};
