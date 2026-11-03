
import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/axios";
import "../../styles/InterviewSession.css";
import ReactMarkdown from "react-markdown";
import VoiceAnswerButton from "./VoiceAnswerButton";

function InterviewSession({ interviewId }) {
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);

  const [answer, setAnswer] = useState("");
  const [answerSubmitted, setAnswerSubmitted] = useState(false);

  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [feedbackLoading, setFeedbackLoading] = useState(false);

  const [error, setError] = useState("");
  const [feedbackError, setFeedbackError] = useState("");

  const loadInterview = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get(
        `/api/interview/interviews/${interviewId}`
      );

      setSession(response.data.data);
      setCurrentIndex(
        response.data.data.current_question_index || 0
      );

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Failed to load interview session."
      );
    } finally {
      setLoading(false);
    }
  }, [interviewId]);

  useEffect(() => {
    loadInterview();
  }, [loadInterview]);

  const loadFeedback = async (questionNumber) => {
    setFeedbackLoading(true);
    setFeedbackError("");

    try {
      const response = await api.post(
        `/api/ai/feedback/interviews/${interviewId}/questions/${questionNumber}`
      );

      setFeedback(response.data.data);

    } catch (err) {
      setFeedbackError(
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Failed to generate AI feedback."
      );
    } finally {
      setFeedbackLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!answer.trim()) {
      setError("Please write your answer before submitting.");
      return;
    }

    const currentQuestion = session.questions[currentIndex];

    if (!currentQuestion) return;

    setSubmitting(true);
    setError("");

    try {
      await api.post(
        `/api/interview/interviews/${interviewId}/answers`,
        {
          question_number: currentQuestion.question_number,
          answer: answer.trim(),
        }
      );

      // Save confirmation before requesting feedback
      setAnswerSubmitted(true);

      // Generate AI feedback for submitted answer
      await loadFeedback(currentQuestion.question_number);

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Answer submission failed."
      );
    } finally {
      setSubmitting(false);
    }
  };

 
const handleNextQuestion = () => {
  const nextIndex = currentIndex + 1;

  if (nextIndex >= session.total_questions) {
    navigate(`/interview/${interviewId}/results`);
    return;
  }

  setCurrentIndex(nextIndex);
  setAnswer("");
  setAnswerSubmitted(false);
  setFeedback(null);
  setFeedbackError("");
  setError("");
};


  const currentQuestion = session?.questions?.[currentIndex];

  if (loading) {
    return <p>Loading interview session...</p>;
  }

  if (error && !session) {
    return <p className="error-message">{error}</p>;
  }

  if (!session) return null;

  if (
    session.status === "completed" ||
    currentIndex >= session.questions.length
  ) {
    return (
      <div className="interview-completed">
        <h2>Interview Completed!</h2>
        <p>You have completed all interview questions.</p>
        <p>Thank you for participating.</p>
      </div>
    );
  }

  return (
    <div className="interview-session">

      <div className="interview-header">
        <h2>AI Mock Interview</h2>

        <p>Role: {session.target_role}</p>

        <p>Type: {session.interview_type}</p>

        <p>Difficulty: {session.difficulty}</p>

        <p>
          Question {currentIndex + 1} of {session.total_questions}
        </p>
      </div>

      <div className="interview-question">
        <h3>
          {currentQuestion.question_number}.{" "}
          {currentQuestion.question}
        </h3>

        <p>Topic: {currentQuestion.topic}</p>

        {currentQuestion.sample_input && (
          <p>Sample Input: {currentQuestion.sample_input}</p>
        )}

        {currentQuestion.sample_output && (
          <p>Sample Output: {currentQuestion.sample_output}</p>
        )}
      </div>

      <div className="answer-section">

        <label htmlFor="candidateAnswer">
          Your Answer
        </label>

        <VoiceAnswerButton
  language="en-IN"
  disabled={answerSubmitted || submitting}
  onTranscript={(transcript) => {
    setAnswer((previousAnswer) =>
      previousAnswer.trim()
        ? `${previousAnswer.trim()} ${transcript}`
        : transcript
    );
  }}
/>

        <textarea
          id="candidateAnswer"
          rows={7}
          maxLength={10000}
          placeholder="Write your answer here..."
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          disabled={answerSubmitted || submitting}
        />

        <p>{answer.length}/10000 characters</p>

        {!answerSubmitted && (
          <button
            onClick={handleSubmitAnswer}
            disabled={submitting || !answer.trim()}
          >
            {submitting ? "Submitting Answer..." : "Submit Answer"}
          </button>
        )}

      </div>

      {error && (
        <p className="error-message">{error}</p>
      )}

      {answerSubmitted && (
        <div className="feedback-section">

          <h2>AI Feedback</h2>

          {feedbackLoading && (
            <p>AI is evaluating your answer...</p>
          )}

          {feedbackError && (
            <>
              <p className="error-message">{feedbackError}</p>

              <button
                onClick={() =>
                  loadFeedback(currentQuestion.question_number)
                }
                disabled={feedbackLoading}
              >
                Retry Feedback
              </button>
            </>
          )}

          {feedback && (
            <>
              <h2>
                Score: {feedback.feedback.score}/10
              </h2>

              <h3>
                Answer Quality: {feedback.feedback.answer_quality}
              </h3>
<h4>Your Submitted Answer</h4>

<div className="submitted-answer">
  <ReactMarkdown>
    {feedback.candidate_answer}
  </ReactMarkdown>
</div>

              <h4>AI Evaluation</h4>
              <p>{feedback.feedback.feedback}</p>

              <h4>Strengths</h4>
              <ul>
                {feedback.feedback.strengths.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>

              <h4>Missing Points</h4>
              <ul>
                {feedback.feedback.missing_points.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>

              <h4>Improvement Suggestions</h4>
              <ul>
                {feedback.feedback.improvement_suggestions.map(
                  (item, index) => (
                    <li key={index}>{item}</li>
                  )
                )}
              </ul>

              <h4>Expected Answer</h4>
              <p>{feedback.expected_answer}</p>

              <button onClick={handleNextQuestion}>
                {currentIndex + 1 >= session.total_questions
                  ? "Finish Interview"
                  : "Next Question"}
              </button>
            </>
          )}

        </div>
      )}

    </div>
  );
}

export default InterviewSession;
