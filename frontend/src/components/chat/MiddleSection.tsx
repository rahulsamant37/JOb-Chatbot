import { useState, useEffect } from "react";
import { useTheme } from "../../context/ThemeContext";
import { FaPaperPlane } from "react-icons/fa";
import XzayognLogo from "../../assets/icons/xzayogn-logo.svg";
import JobCard from "./cards/JobCard";

interface ChatMessage {
  user: string; //'ai' | 'user'
  message: string; // 'ai-query' | 'user-query'
  jobData?: any;
}

const MiddleSection = () => {
  const { theme, currentTheme } = useTheme();
  const [inputValue, setInputValue] = useState<string>("");
  // const [message, setMessage] = useState("");
  const [chatLog, setChatLog] = useState<ChatMessage[]>([]);
  const [isChatLogEmpty, setIsChatLogEmpty] = useState<boolean>(true);

  const API_URL = "http://localhost:8000/search"; // server end-point

  useEffect(() => {
    setIsChatLogEmpty(chatLog.length === 0);
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    console.log("submit");

    // if (inputValue) {
    //   sendMessage(inputValue);
    // }

    // Adding UserMessage to chat::
    const userMessage: ChatMessage = { user: "user", message: inputValue };

    setChatLog((prev) => [...prev, userMessage]);
    setInputValue("");

    // fetch response:
    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "bearer ",
        },
        body: JSON.stringify({
          query: inputValue,
          pagesize: 6,
          chat_history: chatLog.map((msg) => ({
            user: msg.user,
            message: msg.message,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch response");
      }

      const data = await response.json();

      // Differentiate Between Job Data vs AI Text Response
      let aiMessage: ChatMessage;
      // console.log(Array.isArray(data.response?.data));
      // console.log(data.response.data.length > 0);
      if (data.response?.status === "success") {
        if (typeof data.response.data[0] === "object") {
          aiMessage = {
            user: "ai",
            message: "Here are some job recommendations for you:",
            jobData: data.response.data,
          };
        } else {
          aiMessage = {
            user: "ai",
            message:
              data.response.data[0] || "I couldn't find anything relevant.",
            jobData: undefined,
          };
        }
      } else {
        aiMessage = {
          user: "ai",
          message: "No relevant data found.",
          jobData: undefined,
        };
      }

      setChatLog((prev) => [...prev, aiMessage]);
      setIsChatLogEmpty(false);
    } catch (error) {
      console.error("Error Fetching data:", error);
      setChatLog((prev) => [
        ...prev,
        {
          user: "ai",
          message: "Something went wrong. Please try again later.",
        },
      ]);
    }

    // Dummy Data testing...:
    // const data = {
    //   user: "ai",
    //   // message: "Hi how can I help you?",
    //   message:
    //     "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. ",
    //   jobData: {
    //     title: "Software Developer",
    //     company: "google",
    //   },
    // };

    // setChatLog([...chatLogNew, data]);
    // setIsChatLogEmpty(false);
  };

  // const sendMessage = (message: string) => {
  //   const newMessage = {
  //     user: "User",
  //     message: message,
  //     jobData: undefined,
  //   };

  //   setChatLog((prev) => [...prev, newMessage]);
  // };

  // To be added in context...
  // const clearChats = () => {
  //   setChatLog([]);
  //   setIsChatLogEmpty(true);
  // };

  // Dummy Message check...
  // const handleIncomingMessage = (message: string, jobData: undefined) => {
  //   const newMessage = {
  //     user: "ai",
  //     message: message,
  //     jobData: jobData,
  //   };

  //   setChatLog((prev) => [...prev, newMessage]);
  // };

  return (
    <div
      className="flex flex-col flex-1 items-center justify-center text-center pb-6 z-10 px-16"
      style={{
        backgroundColor: currentTheme.chatWindowBg,
        color: currentTheme.primaryFont,
      }}
    >
      {isChatLogEmpty && (
        <div className="mb-6 flex items-center justify-center gap-5 ">
          <img src={XzayognLogo} alt="" className="h-11 w-11" />
          <h3 className="text-3xl pb-1.5">hey i am xzayogn</h3>
        </div>
      )}

      {/* CHAT LOG WINDOW */}
      {!isChatLogEmpty && (
        <div
          className="mt-0 w-full max-w-[822px] h-full overflow-y-auto  no-scrollbar lg:mr-[50px]"
          style={{ maxHeight: "75vh", minHeight: "200px" }}
        >
          {chatLog.map((message, index) => (
            <ChatMessage key={index} {...message} />
          ))}
        </div>
      )}

      <div
        className={`mt-0 w-full max-w-3xl flex items-center  rounded-xl ${
          theme === "light" ? "shadow-xl border border-[#D1D1D1]" : ""
        }`}
        style={{ backgroundColor: currentTheme.chatInputBg }}
      >
        <form
          onSubmit={handleSubmit}
          className="w-full max-w-3xl flex items-center  p-3 "
        >
          <input
            type="text"
            className={`flex-1 bg-transparent outline-none text-lg px-2 ${
              theme === "light"
                ? "placeholder-[#A1A1A1]"
                : "placeholder-[#BABABA]"
            } `}
            placeholder="Message XZAYOGN"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            style={{ color: currentTheme.primaryFont }}
          />
          <button
            type="submit"
            className="p-2 rounded-full transition disabled:opacity-50"
            disabled={!inputValue.trim()}
            style={{
              backgroundColor: currentTheme.sendButton,
              color: currentTheme.chatWindowBg,
            }}
          >
            <FaPaperPlane />
          </button>
        </form>
      </div>

      {/* Suggested Prompts */}
      {/* <div className="mt-4 flex gap-2">
        <button
          className="px-4 py-2 rounded-full border text-sm hover:bg-opacity-20"
          style={{
            color: currentTheme.primaryFont,
            borderColor: currentTheme.secondaryFont,
          }}
        >
          Career in Gaming Industry
        </button>
      </div> */}
    </div>
  );
};

export default MiddleSection;

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
        // <div className="mt-3 h-8 w-8 py-1 font-bold flex items-center justify-center  overflow-visible">
        //   <img src={XzayognLogo} alt="" className="h-8 w-8 object-contain" />
        // </div>
      )}
      <div
        className={`py-3 px-2 text-base ${
          isAgentMessage
            ? "rounded-none max-w-3xl"
            : "py-3 px-5 rounded-2xl rounded-tr-none max-w-2xl "
        }
          
          `}
        style={{
          backgroundColor: isAgentMessage
            ? currentTheme.agentMessageBg
            : currentTheme.userMessageBg,
        }}
      >
        <p className="text-left">{message.message}</p>
        {isAgentMessage && isDataPresent && (
          <div className="grid lg:grid-cols-3 md:grid-cols-2 sm:grid-cols-1 gap-[1rem] my-3 w-full">
            {/* {Array(6)
              .fill(0)
              .map((_, index) => (
                <div key={index} className="flex">
                  <JobCard
                    key={index}
                    title={"Software Developer"}
                    company={"Google"}
                    duration={"2 Months"}
                    location={"Mumbai, India"}
                    salary={"15000/Month"}
                    postedDate={"2025-02-03T12:30:00"}
                    applyUrl={"#"}
                  />
                </div>
              ))} */}
            {message.jobData.map((job: any, index: number) => (
              // <JobCard
              <JobCard
                key={index}
                // title={"Software Developer role frontend backend senior II"}
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
