import { useTheme } from "../../context/ThemeContext";
import XzayognLogo from "../../assets/icons/xzayogn-logo.svg";
import JobCard from "./cards/JobCard";
import TypingAnimation from "../TypingAnimation";

interface ChatMessage {
    user: string; //'ai' | 'user'
    message: string; // 'ai-query' | 'user-query'
    jobData?: any;
    onAnimationUpdate?: () => void;
}

const ChatMessage = (message: ChatMessage) => {
    const { currentTheme } = useTheme();
    const isAgentMessage = message.user === "ai";
    const isDataPresent = message.jobData != undefined;
    
    return (
        <div
            className={`flex ${
                isAgentMessage ? "justify-start items-start" : "justify-end items-end"
            }`}
        >
            {isAgentMessage && (
                <div className="mt-3 flex-none">
                    <img
                        src={XzayognLogo}
                        alt=""
                        className="h-7 w-7 min-w-[32px] min-h-[32px] object-contain"
                    />
                </div>
            )}
            <div
                className={`py-3 px-2 text-base ${
                    isAgentMessage
                        ? "rounded-xl max-w-3xl"
                        : "py-3 px-5 rounded-2xl rounded-tr-none max-w-2xl"
                }`}
                style={{
                    backgroundColor: isAgentMessage
                        ? currentTheme.agentMessageBg
                        : currentTheme.userMessageBg,
                }}
            >
                <p className="text-left">
                    {isAgentMessage ? (
                        <TypingAnimation 
                        text={message.message}
                        onCharacterTyped={message.onAnimationUpdate} />
                    ) : (
                        message.message
                    )}
                </p>

                {isAgentMessage && isDataPresent && (
                    <div className="grid lg:grid-cols-3 md:grid-cols-2 sm:grid-cols-1 gap-[1rem] my-3 w-full">
                        {message.jobData.map((job: any, index: number) => (
                            <JobCard
                                key={index}
                                title={job.title}
                                company={job.company}
                                location={job.location}
                                postedDate="2025-02-02T12:30:00"
                                applyUrl={job.url}
                            />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ChatMessage;