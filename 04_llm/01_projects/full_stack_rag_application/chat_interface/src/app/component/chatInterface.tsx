"use client";
import React, { useState } from "react";
import Image from "next/image";

interface ChatMessage {
  userMessage: string;
  botResponse: string | null;
}

const Chatbot = () => {
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const toggleChatbot = () => {
    setIsOpen(!isOpen);
  };

  const sendMessage = async () => {
    setMessage("");
    setIsLoading(true);

    // Update chatHistory with a temporary loading message
    setChatHistory((prevHistory) => [
      ...prevHistory,
      { userMessage: message, botResponse: null },
    ]);

    try {
      const response = await fetch("/api/assistant", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: message }),
      });

      if (response.ok) {
        const responseData = await response.json();

        setChatHistory((prevHistory) => {
          const updatedHistory = [...prevHistory];
          updatedHistory[updatedHistory.length - 1].botResponse =
            responseData.chat_result;
          return updatedHistory;
        });
      } else {
        console.error("Failed to send message");
      }
    } catch (error) {
      console.error("Error sending message:", error);
    }

    setMessage(""); // Clear the message input
    setIsLoading(false);
  };

  return (
    <div className="fixed bottom-4 right-1 z-50 flex flex-col items-end">
      {isOpen && (
        <div className="chat-container border-2 border-[#1396CE] shadow-md rounded-3xl h-[600px] overflow-auto flex flex-col bg-white">
          <div className="relative bg-[#1396CE] text-white p-4">
            {" "}
            {/* Header Section */}
            <div className="flex items-center justify-between relative ">
              <div className="relative z-10 mt-2 flex items-center">
                <Image
                  src="/Icon.jpeg" // Replace with your actual logo path
                  width={50}
                  height={50}
                  alt="Logo"
                  className="mr-2 rounded-full"
                />
                <h2 className="text-lg font-semibold">HelperBot</h2>
              </div>
            </div>
            <svg
              className="absolute inset-x-0 bottom-0 transform translate-y-14 rotate-180 scale-x-[-1]"
              viewBox="0 0 1440 320"
            >
              <path
                fill="#1396CE"
                fillOpacity="1"
                d="M0,64L48,96C96,128,192,192,288,213.3C384,235,480,213,576,197.3C672,181,768,171,864,160C960,149,1056,139,1152,160C1248,181,1360,210,1480,240L1480,320L0,320Z"
              ></path>
            </svg>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            {chatHistory.map((chat, index) => (
              <div key={index} className="message-container mb-4">
                <div className="flex justify-end">
                  <p className="user-message bg-white border-2 border-[#1396CE] text-gray-800 p-2 rounded-3xl w-64 m-2 max-w-xs sm:max-w-md lg:max-w-lg break-words">
                    {chat.userMessage}
                  </p>
                </div>
                <div className="flex justify-start">
                  {chat.botResponse ? (
                    <p className="bot-message bg-[#1396CE] text-white p-3 rounded-3xl w-64 m-2 max-w-xs sm:max-w-md lg:max-w-lg break-words">
                      {chat.botResponse}
                    </p>
                  ) : (
                    <div className="bot-message bg-[#1396CE] p-3 rounded-3xl m-2 max-w-xs sm:max-w-md lg:max-w-lg flex items-center">
                      <div className="loading-dots">
                        <span>.</span>
                        <span>.</span>
                        <span>.</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
          <div className="input-container p-2 flex items-center">
            <input
              className="flex-grow border-2 border-[#1396CE] p-2 rounded-3xl m-2 focus:outline-none"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Enter your question..."
            />
            <button
              className="bg-[#1396CE] m-2 p-3 shrink-0 rounded-full border-[#1396CE] hover:bg-[#1177A9] focus:outline-none"
              onClick={sendMessage}
            >
              <Image src={"/Vector.svg"} width={18} height={18} alt="vector" />
            </button>
          </div>
        </div>
      )}
      <button
        className="bg-[#1396CE] text-white px-4 py-2 mt-4 rounded-full shadow-md hover:bg-[#1177A9] focus:outline-none"
        onClick={toggleChatbot}
      >
        <Image src={"/chatIcon.svg"} width={35} height={35} alt="vector" />
      </button>
    </div>
  );
};

export default Chatbot;
