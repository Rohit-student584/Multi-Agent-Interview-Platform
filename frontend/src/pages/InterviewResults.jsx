
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../api/axios";
import "../styles/InterviewResults.css";
function InterviewResults() {
  const { interviewId } = useParams();
const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchResults = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await api.get(
          `/api/interview/interviews/${interviewId}/results`
        );

        setResults(response.data.data);

      } catch (err) {
        setError(
          err.response?.data?.detail ||
          "Failed to load interview results."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [interviewId]);

  if (loading) {
    return <p>Loading interview results...</p>;
  }

  if (error) {
    return <p className="error-message">{error}</p>;
  }

  if (!results) {
    return <p>No interview results found.</p>;
  }

  return (
    <div className="results-page">

      <header className="results-header">
        <h1>Interview Results</h1>
        <p>
          {results.target_role} | {results.interview_type} Interview
        </p>
        <p>Difficulty: {results.difficulty}</p>
      </header>
<button
  className="back-dashboard-btn"
  onClick={() => navigate("/dashboard")}
>
  Back to Dashboard
</button>
      <section className="results-overview">

        <div className="result-card">
          <h3>Average Score</h3>
          <h2>
            {results.average_score !== null
              ? `${results.average_score}/10`
              : "N/A"}
          </h2>
        </div>

        <div className="result-card">
          <h3>Percentage</h3>
          <h2>
            {results.percentage !== null
              ? `${results.percentage}%`
              : "N/A"}
          </h2>
        </div>

        <div className="result-card">
          <h3>Questions Answered</h3>
          <h2>
            {results.answered_questions}/{results.total_questions}
          </h2>
        </div>

        <div className="result-card">
          <h3>Evaluated Questions</h3>
          <h2>
            {results.evaluated_questions}/{results.total_questions}
          </h2>
        </div>

      </section>

      <section className="question-results">
        <h2>Question-wise Performance</h2>

        {results.question_results.map((item) => (
          <div
            className="question-result-card"
            key={item.question_number}
          >
            <h3>
              Question {item.question_number}
            </h3>

            <p>{item.question}</p>

            {item.feedback_available ? (
              <>
                <h4>
                  Score: {item.score}/10
                </h4>

                <p>
                  <strong>Answer Quality:</strong>{" "}
                  {item.answer_quality}
                </p>

                <p>
                  <strong>Feedback:</strong>{" "}
                  {item.feedback}
                </p>

                <h4>Strengths</h4>
                <ul>
                  {item.strengths.map((point, index) => (
                    <li key={index}>{point}</li>
                  ))}
                </ul>

                <h4>Missing Points</h4>
                <ul>
                  {item.missing_points.map((point, index) => (
                    <li key={index}>{point}</li>
                  ))}
                </ul>

                <h4>Improvement Suggestions</h4>
                <ul>
                  {item.improvement_suggestions.map((point, index) => (
                    <li key={index}>{point}</li>
                  ))}
                </ul>
              </>
            ) : (
              <p>AI feedback is pending for this question.</p>
            )}
          </div>
        ))}

      </section>

      <section className="overall-feedback">
        <h2>Overall Strengths</h2>

        <ul>
          {results.overall_strengths.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>

        <h2>Areas to Improve</h2>

        <ul>
          {results.overall_missing_points.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>

        <h2>Overall Improvement Suggestions</h2>

        <ul>
          {results.overall_improvement_suggestions.map(
            (item, index) => (
              <li key={index}>{item}</li>
            )
          )}
        </ul>
      </section>

    </div>
  );
}

export default InterviewResults;
