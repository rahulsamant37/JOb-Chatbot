import { useState, useEffect } from "react";

interface TypingAnimationProps {
  text: string;
  speed?: number; // Typing speed in milliseconds
  onTypingEnd?: () => void; // Callback when typing finishes
  onCharacterTyped?: () => void; // Callback when each character is typed
}

const TypingAnimation: React.FC<TypingAnimationProps> = ({
  text,
  speed = 12,
  onTypingEnd,
  onCharacterTyped
}) => {
  const [displayedText, setDisplayedText] = useState(""); // Holds the gradually revealed text
  const [index, setIndex] = useState(0); // Tracks the current letter position

  useEffect(() => {
    if (index < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText((prev) => prev + text[index]); // Add one letter
        setIndex((prev) => prev + 1);
        if (onCharacterTyped) onCharacterTyped();
      }, speed);

      return () => clearTimeout(timeout); // Cleanup timeout on unmount
    } else {
      if (onTypingEnd) onTypingEnd(); // Notify parent when typing is done
    }
  }, [index, text, speed, onTypingEnd]);

  return <span>{displayedText}</span>;
};

export default TypingAnimation;