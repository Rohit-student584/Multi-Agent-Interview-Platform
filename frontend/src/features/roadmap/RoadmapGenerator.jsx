
import { useCallback, useEffect, useState } from "react";
import api from "../../api/axios";
import "../../styles/RoadmapGenerator.css";
function RoadmapGenerator() {
  const [targetRole, setTargetRole] = useState("");
  const [currentSkills, setCurrentSkills] = useState("");
  const [experienceLevel, setExperienceLevel] = useState("Beginner");
  const [durationWeeks, setDurationWeeks] = useState(8);
  const [dailyStudyHours, setDailyStudyHours] = useState(2);
  const [progressLoading, setProgressLoading] = useState(null);
const [progressError, setProgressError] = useState("");

  const [roadmaps, setRoadmaps] = useState([]);
  const [selectedRoadmap, setSelectedRoadmap] = useState(null);

  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchRoadmaps = useCallback(async () => {
    try {
      setHistoryLoading(true);

      const response = await api.get("/api/ai/roadmaps/my");

      setRoadmaps(response.data.roadmaps || []);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Failed to load saved roadmaps."
      );
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRoadmaps();
  }, [fetchRoadmaps]);

  const handleGenerateRoadmap = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");
    setSelectedRoadmap(null);

    try {
      const skillsArray = currentSkills
        .split(",")
        .map((skill) => skill.trim())
        .filter(Boolean);

      const response = await api.post(
        "/api/ai/roadmaps/generate",
        {
          target_role: targetRole.trim(),
          current_skills: skillsArray,
          experience_level: experienceLevel,
          duration_weeks: Number(durationWeeks),
          daily_study_hours: Number(dailyStudyHours),
        }
      );

      setSelectedRoadmap(response.data.data);

      await fetchRoadmaps();

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Failed to generate career roadmap."
      );
    } finally {
      setLoading(false);
    }
  };

  
const handleWeekProgress = async (weekNumber, completed) => {
  if (!selectedRoadmap?.id) return;

  try {
    setProgressLoading(weekNumber);
    setProgressError("");

    const response = await api.patch(
      `/api/ai/roadmaps/${selectedRoadmap.id}/progress`,
      {
        week_number: weekNumber,
        completed: completed,
      }
    );

    const progress = response.data.data;

    setSelectedRoadmap((previous) => ({
      ...previous,
      completed_weeks: progress.completed_weeks,
      completed_count: progress.completed_count,
      progress_percentage: progress.progress_percentage,
    }));

    setRoadmaps((previous) =>
      previous.map((item) =>
        item.id === selectedRoadmap.id
          ? {
              ...item,
              completed_weeks: progress.completed_weeks,
              completed_count: progress.completed_count,
              progress_percentage: progress.progress_percentage,
            }
          : item
      )
    );

  } catch (err) {
    setProgressError(
      err.response?.data?.detail ||
      "Failed to update roadmap progress."
    );
  } finally {
    setProgressLoading(null);
  }frontend/src/features/roadmap/RoadmapGenerator.jsx
};


  const displayRoadmap = selectedRoadmap?.roadmap || selectedRoadmap;
  const completedWeeks = selectedRoadmap?.completed_weeks || [];
const progressPercentage = selectedRoadmap?.progress_percentage ?? 0;

  return (
    <div className="roadmap-generator">

      <div className="roadmap-header">
        <h2>AI Career Roadmap</h2>
        <p>
          Generate a personalized learning roadmap for your career goals.
        </p>
      </div>

      {/* Roadmap Generation Form */}

      <form
        className="roadmap-form"
        onSubmit={handleGenerateRoadmap}
      >

        <div className="roadmap-form-group">
          <label>Target Job Role</label>

          <input
            type="text"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            placeholder="Example: Python Developer"
            minLength={2}
            maxLength={100}
            required
          />
        </div>

        <div className="roadmap-form-group">
          <label>Current Skills</label>

          <textarea
            rows={3}
            value={currentSkills}
            onChange={(e) => setCurrentSkills(e.target.value)}
            placeholder="Python, React, MongoDB, FastAPI, JavaScript"
          />

          <small>Enter skills separated by commas.</small>
        </div>

        <div className="roadmap-form-group">
          <label>Experience Level</label>

          <select
            value={experienceLevel}
            onChange={(e) => setExperienceLevel(e.target.value)}
          >
            <option value="Beginner">Beginner</option>
            <option value="Intermediate">Intermediate</option>
            <option value="Advanced">Advanced</option>
          </select>
        </div>

        <div className="roadmap-form-group">
          <label>Roadmap Duration (Weeks)</label>

          <input
            type="number"
            min="1"
            max="52"
            value={durationWeeks}
            onChange={(e) => setDurationWeeks(e.target.value)}
            required
          />
        </div>

        <div className="roadmap-form-group">
          <label>Daily Study Hours</label>

          <input
            type="number"
            min="0.5"
            max="16"
            step="0.5"
            value={dailyStudyHours}
            onChange={(e) => setDailyStudyHours(e.target.value)}
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
        >
          {loading
            ? "Generating Roadmap..."
            : "Generate Career Roadmap"}
        </button>

      </form>

      {error && (
        <p className="error-message">{error}</p>
      )}

      {/* Generated Roadmap */}

      {displayRoadmap && (
        <div className="generated-roadmap">

          <h2>{displayRoadmap.roadmap_title}</h2>

          <p>{displayRoadmap.summary}</p>
          
<div className="roadmap-progress-section">
  <h3>My Learning Progress</h3>

  <div className="roadmap-progress-track">
    <div
      className="roadmap-progress-fill"
      style={{ width: `${progressPercentage}%` }}
    />
  </div>

  <p>
    {completedWeeks.length} of {displayRoadmap.duration_weeks} weeks completed
    ({progressPercentage}%)
  </p>

  {progressError && (
    <p className="error-message">{progressError}</p>
  )}
</div>


          <h3>Skills to Learn</h3>

          <ul>
            {displayRoadmap.skills_to_learn.map((skill, index) => (
              <li key={index}>{skill}</li>
            ))}
          </ul>

          <h3>Weekly Learning Plan</h3>

          {displayRoadmap.weekly_plan.map((week) => (
            <div
              className="roadmap-week-card"
              key={week.week_number}
            >
                <label className="week-completion">
  <input
    type="checkbox"
    checked={completedWeeks.includes(week.week_number)}
    disabled={progressLoading === week.week_number}
    onChange={(e) =>
      handleWeekProgress(week.week_number, e.target.checked)
    }
  />

  {completedWeeks.includes(week.week_number)
    ? "Week Completed"
    : "Mark Week as Completed"}
</label>
              <h4>
                Week {week.week_number}: {week.focus}
              </h4>

              <p><strong>Topics:</strong></p>

              <ul>
                {week.topics.map((topic, index) => (
                  <li key={index}>{topic}</li>
                ))}
              </ul>

              <p><strong>Practical Tasks:</strong></p>

              <ul>
                {week.practical_tasks.map((task, index) => (
                  <li key={index}>{task}</li>
                ))}
              </ul>

              <p>
                <strong>Project:</strong>{" "}
                {week.project_or_assignment}
              </p>

              <p>
                <strong>Expected Outcome:</strong>{" "}
                {week.expected_learning_outcome}
              </p>
            </div>
          ))}

          <h3>Recommended Projects</h3>

          {displayRoadmap.recommended_projects.map((project, index) => (
            <div className="roadmap-project-card" key={index}>
              <h4>{project.title}</h4>
              <p>{project.description}</p>

              <strong>Skills Covered:</strong>

              <ul>
                {project.skills_covered.map((skill, i) => (
                  <li key={i}>{skill}</li>
                ))}
              </ul>
            </div>
          ))}

          <h3>Learning Milestones</h3>

          <ul>
            {displayRoadmap.milestones.map((milestone, index) => (
              <li key={index}>
                <strong>
                  Week {milestone.expected_week}: {milestone.milestone}
                </strong>
                <p>{milestone.completion_criteria}</p>
              </li>
            ))}
          </ul>

          <h3>Final Goal</h3>
          <p>{displayRoadmap.final_goal}</p>

        </div>
      )}

      {/* Previous Roadmaps */}

      <div className="roadmap-history">

        <h2>My Saved Roadmaps</h2>

        {historyLoading && (
          <p>Loading saved roadmaps...</p>
        )}

        {!historyLoading && roadmaps.length === 0 && (
          <p>No saved roadmaps available.</p>
        )}

        {roadmaps.map((item) => (
          <div className="saved-roadmap-card" key={item.id}>

    <h3>{item.target_role}</h3>

    <p>
      <strong>Level:</strong> {item.experience_level}
    </p>

    <p>
      <strong>Duration:</strong> {item.duration_weeks} weeks
    </p>

    <p>
      <strong>Daily Study:</strong> {item.daily_study_hours} hours
    </p>

    <div className="saved-roadmap-progress">
      <strong>Learning Progress</strong>

      <div className="roadmap-progress-track">
        <div
          className="roadmap-progress-fill"
          style={{
            width: `${item.progress_percentage || 0}%`
          }}
        />
      </div>

      <p>
        {item.completed_count || 0} / {item.duration_weeks} weeks
        completed ({item.progress_percentage || 0}%)
      </p>
    </div>

    <button
      type="button"
      onClick={() => setSelectedRoadmap(item)}
    >
      View Roadmap
    </button>

  </div>

        ))}

      </div>

    </div>
  );
}

export default RoadmapGenerator;
