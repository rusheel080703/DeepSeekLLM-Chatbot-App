import { useEffect, useState } from "react";

const WebSocketClient = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false); // Track connection state

  useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:8080/ws/chat/");
    setSocket(ws);

    ws.onopen = () => {
      console.log("WebSocket connected");
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      console.log("Received from server:", event.data);
      try {
        const data = JSON.parse(event.data);
        setMessages((prevMessages) => [
          ...prevMessages,
          { type: "bot", text: data.message },
        ]);
      } catch (error) {
        console.error("Error parsing message:", error);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setIsConnected(false);
    };

    ws.onclose = (event) => {
      console.log("WebSocket connection closed", event);
      setIsConnected(false);
    };

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const handleSendMessage = () => {
    if (socket && socket.readyState === WebSocket.OPEN && inputMessage) {
      // Append the user's message to the chat window
      setMessages((prevMessages) => [
        ...prevMessages,
        { type: "user", text: inputMessage },
      ]);
      // Send the message as a JSON string with a "message" key.
      socket.send(JSON.stringify({ message: inputMessage }));
      setInputMessage(""); // Clear input after sending
    } else {
      console.log("WebSocket not open yet or message is empty");
    }
  };

  return (
    <div style={styles.chatContainer}>
      <div style={styles.chatWindow}>
        {messages.map((msg, index) => (
          <div
            key={index}
            style={msg.type === "user" ? styles.userMessage : styles.botMessage}
          >
            {msg.text}
          </div>
        ))}
      </div>
      <div style={styles.inputContainer}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type a message..."
          style={styles.input}
        />
        <button
          onClick={handleSendMessage}
          disabled={!isConnected}
          style={styles.sendButton}
        >
          Send
        </button>
      </div>
      {!isConnected && <p>Connecting...</p>}
    </div>
  );
};

const styles = {
  chatContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    width: "100%",
    height: "100vh",
    backgroundColor: "#f1f1f1",
    padding: "10px",
  },
  chatWindow: {
    width: "100%",
    maxWidth: "600px",
    height: "70%",
    overflowY: "scroll",
    backgroundColor: "#fff",
    borderRadius: "8px",
    padding: "20px",
    boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)",
  },
  userMessage: {
    textAlign: "right",
    backgroundColor: "#007bff",
    color: "#fff",
    padding: "10px",
    borderRadius: "10px",
    marginBottom: "10px",
    maxWidth: "80%",
    marginLeft: "auto",
  },
  botMessage: {
    textAlign: "left",
    backgroundColor: "#e1e1e1",
    color: "#000",
    padding: "10px",
    borderRadius: "10px",
    marginBottom: "10px",
    maxWidth: "80%",
    marginRight: "auto",
  },
  inputContainer: {
    display: "flex",
    width: "100%",
    maxWidth: "600px",
    marginTop: "10px",
  },
  input: {
    flex: 1,
    padding: "10px",
    borderRadius: "5px",
    border: "1px solid #ccc",
    marginRight: "10px",
  },
  sendButton: {
    padding: "10px 20px",
    backgroundColor: "#007bff",
    color: "#fff",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
  },
};

export default WebSocketClient;
