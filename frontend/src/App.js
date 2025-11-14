import { useState, useEffect, useRef } from "react";
import "@/App.css";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import { Bot, Send, User, Loader2, AlertCircle } from "lucide-react";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    checkSystemHealth();
    // Only create conversation if database is available
    createConversation();
  }, []);

  const checkSystemHealth = async () => {
    try {
      const response = await axios.get(`${API}/health`);
      setSystemStatus(response.data);
      
      if (!response.data.agent_initialized) {
        toast.error("AI agents not initialized. Please configure API keys in backend .env file.");
      }
    } catch (error) {
      console.error("Health check failed:", error);
      toast.error("Failed to connect to backend");
    }
  };

  const createConversation = async () => {
    try {
      const response = await axios.post(`${API}/conversations`);
      setConversationId(response.data.id);
    } catch (error) {
      console.error("Failed to create conversation:", error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: "user",
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      const response = await axios.post(`${API}/chat`, {
        message: inputMessage,
        conversation_id: conversationId
      });

      const assistantMessage = {
        id: response.data.message.id,
        role: "assistant",
        content: response.data.message.content,
        agent: response.data.agent,
        timestamp: response.data.message.timestamp,
        metadata: response.data.metadata
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      
      const errorMessage = {
        id: Date.now().toString(),
        role: "assistant",
        content: error.response?.data?.detail || "Sorry, I encountered an error. Please make sure the API keys are configured correctly.",
        timestamp: new Date().toISOString(),
        error: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
      toast.error("Failed to send message");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo-container">
              <Bot className="logo-icon" size={32} />
            </div>
            <div>
              <h1 className="header-title">AI Hotel Assistant</h1>
              <p className="header-subtitle">Multi-Agent System with MCP Servers</p>
            </div>
          </div>
          
          <div className="status-indicator">
            {systemStatus?.agent_initialized ? (
              <div className="status-badge status-active">
                <div className="status-dot"></div>
                <span>Active</span>
              </div>
            ) : (
              <div className="status-badge status-inactive">
                <AlertCircle size={14} />
                <span>Not Configured</span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Chat Area */}
      <main className="main-content">
        <div className="chat-container">
          <ScrollArea className="messages-area">
            <div className="messages-wrapper">
              {messages.length === 0 ? (
                <div className="welcome-screen">
                  <div className="welcome-icon">
                    <Bot size={64} />
                  </div>
                  <h2 className="welcome-title">Welcome to AI Hotel Assistant</h2>
                  <p className="welcome-text">
                    I'm powered by LangGraph with multi-agent workflows and MCP servers.
                    <br />Ask me to search for hotels or make bookings!
                  </p>
                  
                  <div className="example-prompts">
                    <p className="example-title">Try asking:</p>
                    <div className="example-grid">
                      <button 
                        className="example-button"
                        onClick={() => setInputMessage("Find hotels in Paris for 2 guests")}
                        data-testid="example-search-hotels"
                      >
                        "Find hotels in Paris for 2 guests"
                      </button>
                      <button 
                        className="example-button"
                        onClick={() => setInputMessage("Show me luxury hotels in Tokyo with high ratings")}
                        data-testid="example-luxury-hotels"
                      >
                        "Show me luxury hotels in Tokyo with high ratings"
                      </button>
                      <button 
                        className="example-button"
                        onClick={() => setInputMessage("Book hotel_1 from Jan 15 to Jan 20 for John Doe")}
                        data-testid="example-book-hotel"
                      >
                        "Book hotel_1 from Jan 15 to Jan 20 for John Doe"
                      </button>
                      <button 
                        className="example-button"
                        onClick={() => setInputMessage("Show me my profile and rewards for customer_1")}
                        data-testid="example-customer-profile"
                      >
                        "Show me my profile and rewards for customer_1"
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`message ${message.role === "user" ? "message-user" : "message-assistant"}`}
                    data-testid={`message-${message.role}`}
                  >
                    <Avatar className="message-avatar">
                      <AvatarFallback>
                        {message.role === "user" ? <User size={20} /> : <Bot size={20} />}
                      </AvatarFallback>
                    </Avatar>
                    
                    <div className="message-content-wrapper">
                      <div className="message-header">
                        <span className="message-sender">
                          {message.role === "user" ? "You" : "Assistant"}
                        </span>
                        {message.agent && (
                          <span className="agent-badge" data-testid="agent-badge">
                            {message.agent.replace('_', ' ')}
                          </span>
                        )}
                      </div>
                      <div className="message-text">
                        {message.content}
                      </div>
                    </div>
                  </div>
                ))
              )}
              
              {isLoading && (
                <div className="message message-assistant" data-testid="loading-message">
                  <Avatar className="message-avatar">
                    <AvatarFallback>
                      <Bot size={20} />
                    </AvatarFallback>
                  </Avatar>
                  <div className="message-content-wrapper">
                    <div className="loading-indicator">
                      <Loader2 className="animate-spin" size={16} />
                      <span>Processing your request...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          {/* Input Area */}
          <div className="input-container">
            <Card className="input-card">
              <form onSubmit={sendMessage} className="input-form">
                <Input
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Ask me to search hotels or make bookings..."
                  disabled={isLoading}
                  className="message-input"
                  data-testid="chat-input"
                />
                <Button 
                  type="submit" 
                  disabled={isLoading || !inputMessage.trim()}
                  className="send-button"
                  data-testid="send-button"
                >
                  {isLoading ? (
                    <Loader2 className="animate-spin" size={20} />
                  ) : (
                    <Send size={20} />
                  )}
                </Button>
              </form>
            </Card>
            
            <p className="powered-by" data-testid="powered-by-text">
              Powered by LangGraph • {systemStatus?.llm_provider?.toUpperCase() || 'LLM'} • MCP Servers
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;