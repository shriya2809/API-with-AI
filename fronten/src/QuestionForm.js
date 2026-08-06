import { useState } from "react";
import axios from "axios";
import { BounceLoader } from "react-spinners";

const api = axios.create({
  baseURL: "http://localhost:8000"
});

function QuestionForm() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await api.post('/chat', { message: question });
      setAnswer(response.data.answer || "No answer returned.");
    } catch (err) {
      console.error("Chat error:", err);
      setAnswer("Error getting response.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleIndexing = async (e) => {
    e.preventDefault();
    setAnswer('');
    setIsLoading(true);
    try {
      const response = await api.post('/indexing', null, { params: { url: question } });
      // Fixed: /indexing returns response.data.response
      setAnswer(response.data.response || response.data.message || "Successfully indexed!");
    } catch (err) {
      console.error("Indexing error:", err);
      setAnswer(err.response?.data?.error || "Failed to index URL. Ensure it starts with http:// or https://");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="main-container">
      <form className="form">
        <input 
          className="form-input" 
          type="text" 
          value={question} 
          onChange={(e) => setQuestion(e.target.value)} 
          placeholder="Ask a question or enter a URL..."
        />
        <div className="buttons-container">
          <button className="form-button" type="submit" onClick={handleSubmit}>Q&A</button>
          <button className="form-button" type="button" style={{backgroundColor: 'red'}} onClick={handleIndexing}>Index</button>
        </div>
      </form>
      {isLoading && (
        <div className="loader-container">
          <BounceLoader color="#3498db" />
        </div>
      )}
      <div>
        <h2>Response:</h2>
        <p>{answer}</p>
      </div>
    </div>
  );
}

export default QuestionForm;