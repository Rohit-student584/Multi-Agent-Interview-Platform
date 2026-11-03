
import { useCallback, useEffect, useState } from "react";
import api from "../../api/axios";
import "../../styles/DashboardAnalytics.css";
function DashboardAnalytics() {
  const [analytics, setAnalytics] = useState({
    totalInterviews: 0,
    averageScore: null,
    totalRoadmaps: 0,
    roadmapProgress: 0,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchAnalytics = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const [interviewResponse, roadmapResponse] =
        await Promise.all([
          api.get("/api/interview/interviews/my"),
          api.get("/api/ai/roadmaps/my"),
        ]);

      const interviews =
        interviewResponse.data.interviews || [];

      const roadmaps =
        roadmapResponse.data.roadmaps || [];

      // Calculate average interview score
    const scoredInterviews = interviews.filter(
  (interview) =>
    interview.status === "completed" &&
    typeof interview.average_score === "number"
);

      const averageScore = scoredInterviews.length
        ? Number(
            (
              scoredInterviews.reduce(
                (total, interview) =>
                  total + interview.average_score,
                0
              ) / scoredInterviews.length
            ).toFixed(2)
          )
        : null;

      // Calculate overall roadmap progress
      const totalWeeks = roadmaps.reduce(
        (total, roadmap) =>
          total + roadmap.duration_weeks,
        0
      );

      const completedWeeks = roadmaps.reduce(
        (total, roadmap) =>
          total + (roadmap.completed_count || 0),
        0
      );

      const roadmapProgress = totalWeeks
        ? Number(
            ((completedWeeks / totalWeeks) * 100).toFixed(2)
          )
        : 0;

      setAnalytics({
        totalInterviews: interviews.length,
        averageScore,
        totalRoadmaps: roadmaps.length,
        roadmapProgress,
      });

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Failed to load dashboard analytics."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  if (loading) {
    return <p>Loading dashboard analytics...</p>;
  }

  if (error) {
    return (
      <div className="dashboard-analytics">
        <p className="error-message">{error}</p>
        <button onClick={fetchAnalytics}>Retry</button>
      </div>
    );
  }

  const cards = [
    {
      title: "Total Interviews",
      value: analytics.totalInterviews,
      description: "All interview attempts",
    },
    {
      title: "Average Score",
      value:
        analytics.averageScore !== null
          ? `${analytics.averageScore}/10`
          : "N/A",
      description: "Across evaluated interviews",
    },
    {
      title: "Roadmaps Created",
      value: analytics.totalRoadmaps,
      description: "Personalized career roadmaps",
    },
    {
      title: "Roadmap Progress",
      value: `${analytics.roadmapProgress}%`,
      description: "Combined learning progress",
    },
  ];

  return (
    <section className="dashboard-analytics">

      <div className="analytics-header">
        <div>
          <h2>Dashboard Overview</h2>
          <p>Track your interview and learning performance.</p>
        </div>

        <button onClick={fetchAnalytics}>
          Refresh
        </button>
      </div>

      <div className="analytics-grid">

        {cards.map((card) => (
          <div className="analytics-card" key={card.title}>
            <h3>{card.title}</h3>

            <h2>{card.value}</h2>

            <p>{card.description}</p>
          </div>
        ))}

      </div>

    </section>
  );
}

export default DashboardAnalytics;
