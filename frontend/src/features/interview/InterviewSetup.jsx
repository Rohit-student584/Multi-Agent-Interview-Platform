
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/axios";
import "../../styles/InterviewSetup.css";

function InterviewSetup() {
  const navigate = useNavigate();

  const [interviewType, setInterviewType] = useState("Technical");
  const [targetRole, setTargetRole] = useState("Python Developer");
  const [difficulty, setDifficulty] = useState("Beginner");
  const [totalQuestions, setTotalQuestions] = useState(5);

  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (targetRole.trim().length < 2) {
      setError("Please enter a valid target job role.");
      return;
    }

    setLoading(true);

    try {
      let currentSessionId = sessionId;

      // Create interview session
      if (!currentSessionId) {
        const sessionResponse = await api.post(
          "/api/interview/interviews",
          {
            interview_type: interviewType,
            target_role: targetRole.trim(),
            difficulty,
            total_questions: Number(totalQuestions),
          }
        );

        currentSessionId = sessionResponse.data.id;
        setSessionId(currentSessionId);
      }

      // Generate and save questions using AI
      await api.post(
        `/api/ai/interviews/sessions/${currentSessionId}/generate`
      );

      // Navigate to interview screen
      navigate(`/interview/${currentSessionId}`);

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Failed to start interview. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="interview-setup">

      <h2>Start New Interview</h2>

      <p>Configure your AI mock interview.</p>

      <form onSubmit={handleSubmit}>

        <div className="form-group">
          <label htmlFor="interviewType">
            Interview Type
          </label>

          <select
            id="interviewType"
            value={interviewType}
            onChange={(e) => setInterviewType(e.target.value)}
            disabled={loading || Boolean(sessionId)}
          >
            <option value="HR">HR Interview</option>
            <option value="Technical">Technical Interview</option>
            <option value="Coding">Coding Interview</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="targetRole">
            Target Job Role
          </label>

          <input
            id="targetRole"
            type="text"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            placeholder="e.g. Python Developer"
            disabled={loading || Boolean(sessionId)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="difficulty">
            Difficulty Level
          </label>

          <select
            id="difficulty"
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            disabled={loading || Boolean(sessionId)}
          >
            <option value="Beginner">Beginner</option>
            <option value="Intermediate">Intermediate</option>
            <option value="Advanced">Advanced</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="totalQuestions">
            Total Questions
          </label>

          <input
            id="totalQuestions"
            type="number"
            min="1"
            max="20"
            value={totalQuestions}
            onChange={(e) => setTotalQuestions(e.target.value)}
            disabled={loading || Boolean(sessionId)}
            required
          />
        </div>

        {error && (
          <p className="error-message">{error}</p>
        )}

        <button
          type="submit"
          disabled={loading}
        >
          {loading
            ? "Preparing Your Interview..."
            : sessionId
              ? "Retry Starting Interview"
              : "Generate Questions & Start Interview"}
        </button>

      </form>

    </div>
  );
}

export default InterviewSetup;
