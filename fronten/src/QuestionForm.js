import { useState } from 'react';

function QuestionForm() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Your question: ", question);
  }

  return (
    <form>
      <input type="text" value={question} onChange={(e) => setQuestion(e.target.value)} />
      <button type="submit" onClick={handleSubmit}>Submit</button>
    </form>
  );
}

export default QuestionForm;