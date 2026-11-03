
import { useCallback, useEffect, useState } from "react";
import api from "../../api/axios";
import "../../styles/ResumeList.css";

function ResumeList() {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [targetRole, setTargetRole] = useState("Software Engineer");
  const [analyzingId, setAnalyzingId] = useState(null);
  const [analyses, setAnalyses] = useState({});
  const [analysisErrors, setAnalysisErrors] = useState({});

  // Fetch resumes and their previously saved AI analyses
  const fetchResumes = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/api/resume/resumes/my");
      const userResumes = response.data.resumes || [];

      setResumes(userResumes);

      const analysisEntries = await Promise.all(
        userResumes.map(async (resume) => {
          try {
            const analysisResponse = await api.get(
              `/api/ai/resumes/${resume.id}/analysis`
            );

            return [
              resume.id,
              analysisResponse.data.data.analysis,
            ];
          } catch (err) {
            if (err.response?.status !== 404) {
              console.error(
                `Could not load analysis for ${resume.filename}:`,
                err.response?.data || err.message
              );
            }

            return [resume.id, null];
          }
        })
      );

      setAnalyses(
        Object.fromEntries(
          analysisEntries.filter(([, analysis]) => analysis)
        )
      );

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Failed to load resumes."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchResumes();
  }, [fetchResumes]);

  // Generate a new resume analysis
  const handleAnalyze = async (resumeId) => {
    if (!targetRole.trim()) {
      setAnalysisErrors((prev) => ({
        ...prev,
        [resumeId]: "Please enter a target job role.",
      }));
      return;
    }

    setAnalyzingId(resumeId);

    setAnalysisErrors((prev) => ({
      ...prev,
      [resumeId]: "",
    }));

    try {
      const response = await api.post(
        `/api/ai/resumes/${resumeId}/analyze`,
        {
          target_role: targetRole.trim(),
        }
      );

      setAnalyses((prev) => ({
        ...prev,
        [resumeId]: response.data.data.analysis,
      }));

    } catch (err) {
      setAnalysisErrors((prev) => ({
        ...prev,
        [resumeId]:
          err.response?.data?.detail ||
          err.response?.data?.message ||
          "Resume analysis failed.",
      }));
    } finally {
      setAnalyzingId(null);
    }
  };

  if (loading) {
    return <p>Loading your resumes and saved analyses...</p>;
  }

  return (
    <div className="resume-list">

      <div className="resume-list-header">
        <h2>My Resumes</h2>

        <button onClick={fetchResumes}>
          Refresh
        </button>
      </div>

      {error && (
        <p className="error-message">{error}</p>
      )}

      <div className="target-role-input">
        <label htmlFor="targetRole">
          Target Job Role
        </label>

        <input
          id="targetRole"
          type="text"
          value={targetRole}
          onChange={(e) => setTargetRole(e.target.value)}
          placeholder="e.g. Junior Python Developer"
        />
      </div>

      {!error && resumes.length === 0 && (
        <p>You have not uploaded any resumes yet.</p>
      )}

      <div className="resume-items">

        {resumes.map((resume) => {
          const analysis = analyses[resume.id];
          const isAnalyzing = analyzingId === resume.id;

          return (
            <div className="resume-item" key={resume.id}>

              <h3>{resume.filename}</h3>

              <p>
                File type: {resume.file_type.toUpperCase()}
              </p>

              <p>
                Extracted characters: {resume.extracted_characters}
              </p>

              <p>
                Uploaded:{" "}
                {resume.created_at
                  ? new Date(resume.created_at).toLocaleString()
                  : "Date unavailable"}
              </p>

              <button
                onClick={() => handleAnalyze(resume.id)}
                disabled={isAnalyzing}
              >
                {isAnalyzing
                  ? "Analyzing Resume..."
                  : analysis
                    ? "Analyze Again"
                    : "Analyze Resume"}
              </button>

              {analysisErrors[resume.id] && (
                <p className="error-message">
                  {analysisErrors[resume.id]}
                </p>
              )}

              {analysis && (
                <div className="analysis-result">

                  <h3>AI Resume Analysis</h3>

                  <h2>
                    ATS Score: {analysis.estimated_ats_score}/100
                  </h2>

                  <p>{analysis.overall_summary}</p>

                  <h4>Strengths</h4>
                  <ul>
                    {analysis.strengths.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>

                  <h4>Weaknesses</h4>
                  <ul>
                    {analysis.weaknesses.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>

                  <h4>Missing Keywords</h4>
                  <ul>
                    {analysis.missing_keywords.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>

                  <h4>Improvement Suggestions</h4>
                  <ul>
                    {analysis.improvement_suggestions.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>

                  <h4>Rewritten Professional Summary</h4>
                  <p>{analysis.rewritten_summary}</p>

                  <h4>Recommended Job Roles</h4>
                  <ul>
                    {analysis.recommended_roles.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>

                </div>
              )}

            </div>
          );
        })}

      </div>
    </div>
  );
}

export default ResumeList;
