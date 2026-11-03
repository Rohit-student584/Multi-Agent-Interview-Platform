
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/axios";
import "../../styles/InterviewHistory.css";

function InterviewHistory() {
  const navigate = useNavigate();

  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get(
        "/api/interview/interviews/my"
      );

      setInterviews(response.data.interviews || []);

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Failed to load interview history."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const formatDate = (date) => {
    if (!date) return "Not available";

    return new Date(date).toLocaleString();
  };

  if (loading) {
    return <p>Loading interview history...</p>;
  }

  return (
    <div className="interview-history">

      <div className="history-header">
        <div>
          <h2>My Interview History</h2>
          <p>View your previous interview attempts and scores.</p>
        </div>

        <button onClick={fetchHistory}>
          Refresh
        </button>
      </div>

      {error && (
        <p className="error-message">{error}</p>
      )}

      {!error && interviews.length === 0 && (
        <p>You have not completed any interviews yet.</p>
      )}

      <div className="history-list">

        {interviews.map((interview) => (
          <div
            className="history-card"
            key={interview.id}
          >
            <h3>{interview.target_role}</h3>

            <p>
              <strong>Type:</strong>{" "}
              {interview.interview_type}
            </p>

            <p>
              <strong>Difficulty:</strong>{" "}
              {interview.difficulty}
            </p>

         <p className="status-row">
  <strong>Status:</strong>

  <span
    className={`status-badge ${
      interview.status === "completed"
        ? "completed"
        : "in-progress"
    }`}
  >
    {interview.status === "completed"
      ? "Completed"
      : "In Progress"}
  </span>
</p>

            <p>
              <strong>Date:</strong>{" "}
              {formatDate(interview.created_at)}
            </p>

            <p>
              <strong>Questions:</strong>{" "}
              {interview.answered_questions}/
              {interview.total_questions}
            </p>

            <p>
              <strong>Evaluated:</strong>{" "}
              {interview.evaluated_questions}/
              {interview.total_questions}
            </p>

            <p>
              <strong>Average Score:</strong>{" "}
              {interview.average_score !== null
                ? `${interview.average_score}/10`
                : "Pending"}
            </p>

            <p>
              <strong>Percentage:</strong>{" "}
              {interview.percentage !== null
                ? `${interview.percentage}%`
                : "Pending"}
            </p>

            <button
              onClick={() =>
                navigate(
                  interview.status === "completed"
                    ? `/interview/${interview.id}/results`
                    : `/interview/${interview.id}`
                )
              }
            >
              {interview.status === "completed"
                ? "View Results"
                : "Continue Interview"}
            </button>

          </div>
        ))}

      </div>
    </div>
  );
}

export default InterviewHistory;
