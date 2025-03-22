"use client";
import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown"; // Import react-markdown
import remarkGfm from "remark-gfm"; // Import plugin for GitHub-flavored Markdown (optional)

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false); // New loading state
  const inputRef = useRef(null); // Reference to the input element
  const chatEndRef = useRef(null); // Reference to the end of the chat container

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

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-900 text-gray-100">
      <div className="w-full max-w-2xl flex flex-col h-4/5 bg-gray-800 shadow-lg rounded-lg overflow-hidden">
        <div className="flex-1 p-4 overflow-y-auto space-y-4 flex flex-col">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`inline-block max-w-[75%] p-3 rounded-lg ${
                msg.role === "user"
                  ? "bg-blue-600 text-white self-end"
                  : msg.role === "assistant"
                  ? "bg-gray-700 text-gray-100 self-start"
                  : "bg-red-600 text-white self-start"
              }`}
            >
              {/* Render Markdown content */}
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
            </div>
          ))}
          {/* Typing Indicator */}
          {loading && (
            <div className="inline-block max-w-[75%] p-3 rounded-lg bg-gray-700 text-gray-100 self-start">
              Typing...
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
            disabled={loading} // Disable input when loading
          />
          {input.trim() && (
            <button
              onClick={sendMessage}
              className="ml-4 px-4 py-2 bg-blue-600 text-white rounded-lg"
              disabled={loading} // Disable button when loading
            >
              {loading ? "Sending..." : "Send"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}