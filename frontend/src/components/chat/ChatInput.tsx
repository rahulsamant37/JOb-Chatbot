import { useState } from "react";

// icons
import { FaPaperPlane } from "react-icons/fa";

const ChatInput = ({ onSend }: { onSend: (message: string) => void }) => {
  const [message, setMessage] = useState("");

  const handleSend = () => {
    if (message.trim()) {
      onSend(message);
      setMessage("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="fixed bottom-0 w-full flex justify-center p-10 dark:bg-gray-900">
      <div className="flex w-full max-w-2xl bg-gray-200 dark:bg-[#383A40] rounded-xl p-3">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyPress} //Enter-to-send
          placeholder="Type your message..."
          className="flex-1 bg-transparent outline-none text-black dark:text-white"
        />
        <button onClick={handleSend} className="ml-2 text-[#BABABA] text-xl">
          <FaPaperPlane />
        </button>
      </div>
    </div>
  );
};

export default ChatInput;
