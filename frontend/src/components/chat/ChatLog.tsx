import { useState } from "react";
import { useTheme } from "../../context/ThemeContext";
import JobCards from "./cards/JobCards";

const ChatLog = () => {
  const { currentTheme } = useTheme();
  const [messages, setMessages] = useState<
    { text: string; sender: "user" | "ai"; JobData?: any[] }[]
  >([]);

  const handleNewMessage = (message: string) => {
    setMessages([...messages, { text: message, sender: "user" }]);

    // Async: use this "message to send request of query to agent/server here... "
    // example testing here....
    setTimeout(() => {
      const simulatedResponse = {
        text: "Here are some job recommendations:",
        sender: "ai",
        jobData: [
          { title: "Software Engineer", company: "Google", location: "Remote" },
          { title: "Data Scientist", company: "Meta", location: "New York" },
        ],
      };
      setMessages((prev) => [...prev, simulatedResponse]);
    }, 1000);
  };

  return (
    <div
      className="flex flex-col flex-1 px-6 py-4 overflow-y-auto mt-16 mb-20"
      style={{
        backgroundColor: currentTheme.chatWindowBg,
        color: currentTheme.primaryFont,
      }}
    >
      {messages.map((msg, index) => (
        <div
          key={index}
          className={`my-2 ${
            msg.sender === "user" ? "text-right" : "text-left"
          }`}
        >
          <div className={`p-3 rounded-lg inline-block`}>{msg.text}</div>
          {msg.sender === "ai" && msg.jobData && (
            <JobCards jobs={msg.jobData} />
          )}
        </div>
      ))}
    </div>
  );
};

export default ChatLog;
