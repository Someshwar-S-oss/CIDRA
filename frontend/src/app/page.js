"use client";
import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown"; // Import react-markdown
import remarkGfm from "remark-gfm"; // Import plugin for GitHub-flavored Markdown

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);
  const [progress, setProgress] = useState("");
  const [videoSrc, setVideoSrc] = useState("");
  const [isFileUploaded, setIsFileUploaded] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || loading) return; // Prevent sending if already loading

    setInput(""); // Clear input field immediately
    setLoading(true); // Set loading to true

    // Add user message to the chat
    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);

    try {
      // Send message to the backend
      const response = await fetch("http://127.0.0.1:5000/api/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const data = await response.json();
      const botMessage = { role: "assistant", content: data.response };

      // Add bot response to the chat
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      // Add error message to the chat
      setMessages((prev) => [
        ...prev,
        { role: "error", content: "Error sending message" },
      ]);
    } finally {
      setLoading(false); // Set loading to false after response
    }
  };

  // Automatically focus the input field when loading becomes false
  useEffect(() => {
    if (!loading && inputRef.current) {
      inputRef.current.focus();
    }
  }, [loading]);

  // Scroll to the bottom of the chatbox when messages change
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleFileUpload = async (event) => {
    const file = fileInputRef.current.files[0];
    if (!file) return;
  
    const formData = new FormData();
    formData.append("file", file);
  
    try {
      const response = await fetch("http://127.0.0.1:5000/api/upload", {
        method: "POST",
        body: formData,
      });
  
      if (!response.ok) {
        throw new Error("Failed to upload file");
      }
  
      const data = await response.json(); // Read the response body once
      const filePath = data.file_path;
  
      // Display the file path in the UI
      document.getElementById("filePathDisplay").textContent = `${filePath}`;
  
      console.log("File uploaded successfully:", data);
  
      setIsFileUploaded(true);
      setVideoSrc("http://127.0.0.1:5000/runs/detect/track/video.avi");

    } catch (error) {
      console.error("Error uploading file:", error);
    }
  };

  return (
    <div className="flex flex-row max-lg:flex-col items-center justify-between h-screen bg-gray-900 text-gray-100">
      <div className="w-80 h-full bg-gray-800 shadow-lg rounded-xl p-4 flex flex-col overflow-hidden items-center">
        <button
          className="bg-blue-600 px-4 py-2 rounded-xl hover:bg-blue-700 mb-4"
          onClick={async () => {
            try {
              const response = await fetch("http://127.0.0.1:5000/api/clear", {
                method: "POST",
              });
              if (!response.ok) {
                throw new Error("Failed to clear chat");
              }
              setMessages([]); // Clear the messages in the frontend

              // Clear the file name displayed in the UI
              document.getElementById("filePathDisplay").textContent = "";

              // Reset the file input field
              if (fileInputRef.current) {
                fileInputRef.current.value = null;
              }
              window.location.reload();
            } catch (error) {
              console.error("Error clearing chat:", error);
            }
          }}
        >
          New Chat +
        </button>
        <div className="w-full mt-25 h-10 mb-16">
          <label
            htmlFor="example1"
            className="mb-1 block text-md font-medium text-center text-gray-100"
          >
            Upload file
          </label>
          <input
            id="example1"
            type="file"
            ref={fileInputRef}
            className="p-3 rounded-md mt-2 block w-full text-sm text-black bg-gray-700 file:mr-4 file:rounded-md file:border-0 file:bg-blue-600 file:py-2 file:px-4 file:text-sm file:font-semibold file:text-white hover:file:bg-blue-800 focus:outline-none disabled:pointer-events-none disabled:opacity-60"
          />
        </div>
        <button
          className="bg-blue-600 px-4 py-2 rounded-xl hover:bg-blue-700 mb-4"
          onClick={handleFileUpload}
        >
          Upload
        </button>
      </div>

      {/* Chatbox */}
      <div className="w-full max-w-2xl flex flex-col h-4/5 bg-gray-800 shadow-lg rounded-xl overflow-hidden">
        <div className="flex-1 p-4 overflow-y-auto space-y-4 flex flex-col">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`inline-block max-w-[75%] p-3 rounded-xl ${
                msg.role === "user"
                  ? "bg-blue-600 text-white self-end"
                  : msg.role === "assistant"
                  ? "bg-gray-700 text-gray-100 self-start"
                  : "bg-red-600 text-white self-start"
              }`}
            >
              {/* Render Markdown content */}
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {msg.content}
              </ReactMarkdown>
            </div>
          ))}
          {/* Typing Indicator */}
          {loading && (
            <div className="inline-block max-w-[75%] p-3 rounded-lg bg-gray-700 text-gray-100 self-start">
              <span className="typing-dots">
                <span>.</span>
                <span>.</span>
                <span>.</span>
              </span>
            </div>
          )}
          {/* Scroll Anchor */}
          <div ref={chatEndRef}></div>
        </div>

        {/* Input Section */}
        <div className="flex items-center p-4 border-t border-gray-700">
          <input
            ref={inputRef} // Attach the ref to the input element
            type="text"
            className="flex-1 p-2 bg-gray-700 text-gray-100 border border-gray-600 rounded-lg focus:outline-none focus:ring focus:ring-blue-500"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            disabled={loading || !isFileUploaded} // Disable input when loading
          />
          {input.trim() && (
            <button
              onClick={sendMessage}
              className="ml-4 px-4 py-2 bg-blue-600 text-white rounded-lg"
              disabled={loading || !isFileUploaded} // Disable button when loading
            >
              {loading ? "Sending..." : "Send"}
            </button>
          )}
        </div>
      </div>
      <div className="w-110 h-full bg-gray-800 rounded-xl">
        {isFileUploaded && videoSrc && ( // Conditionally render the video element
          <video className="w-full h-auto" controls>
            <source
              src={videoSrc} 
              type="video/mp4"
            ></source>
            Your browser does not support the video tag.
          </video>
        )}
        <h1 className="text-xl text-center text-white p-4">Video Analytics</h1>
        <div className="flex flex-col p-4">
          <span>
            File Name: <span id="filePathDisplay"></span>
          </span>
          {/* <span>{progress}</span> */}
        </div>
      </div>
    </div>
  );
}