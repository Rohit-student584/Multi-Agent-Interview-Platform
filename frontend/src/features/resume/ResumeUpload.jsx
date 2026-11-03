import { useState } from "react";
import api from "../../api/axios";
import "../../styles/ResumeUpload.css";

function ResumeUpload() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0];

    setError("");
    setResult(null);
    setFile(selectedFile || null);

    if (!selectedFile) return;

    const extension = selectedFile.name
      .split(".")
      .pop()
      .toLowerCase();

    if (!["pdf", "docx"].includes(extension)) {
      setError("Only PDF and DOCX files are supported.");
      setFile(null);
      e.target.value = "";
      return;
    }

    if (selectedFile.size > 5 * 1024 * 1024) {
      setError("File size must not exceed 5 MB.");
      setFile(null);
      e.target.value = "";
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();

    if (!file) {
      setError("Please select a resume first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await api.post(
        "/api/resume/resumes/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setResult(response.data);
      setFile(null);
      e.target.reset();

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Resume upload failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="resume-upload">

      <h2>Upload Your Resume</h2>

      <p>Upload your resume in PDF or DOCX format.</p>

      <form onSubmit={handleUpload}>

        <input
          type="file"
          accept=".pdf,.docx"
          onChange={handleFileChange}
          disabled={loading}
        />

        {file && (
          <p>Selected file: {file.name}</p>
        )}

        {error && (
          <p className="error-message">{error}</p>
        )}

        <button
          type="submit"
          disabled={loading || !file}
        >
          {loading ? "Uploading..." : "Upload Resume"}
        </button>

      </form>

      {result && (
        <div className="upload-success">

          <h3>Resume Uploaded Successfully!</h3>

          <p>Filename: {result.filename}</p>

          <p>Resume ID: {result.resume_id}</p>

          <p>
            Extracted Characters: {result.extracted_characters}
          </p>

        </div>
      )}

    </div>
  );
}

export default ResumeUpload;