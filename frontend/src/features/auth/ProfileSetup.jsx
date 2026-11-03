
import { useEffect, useState } from "react";
import api from "../../api/axios";
import "../../styles/ProfileSetup.css";
import ProfileImage from "./ProfileImage";

function ProfileSetup() {
  const [name, setName] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [skills, setSkills] = useState("");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Fetch existing user profile
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await api.get("/api/users/me");
        const profile = response.data;

        setName(profile.name || "");
        setTargetRole(profile.target_role || "");
        setSkills((profile.skills || []).join(", "));
      } catch (err) {
        setError(
          err.response?.data?.detail ||
          "Failed to load profile."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  // Update user profile
  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (name.trim().length < 2) {
      setError("Name must contain at least 2 characters.");
      return;
    }

    setSaving(true);

    try {
      const skillsArray = skills
        .split(",")
        .map((skill) => skill.trim())
        .filter(Boolean);

      await api.put("/api/users/me", {
        name: name.trim(),
        target_role: targetRole.trim() || null,
        skills: [...new Set(skillsArray)],
      });

      setSuccess("Profile updated successfully!");

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Failed to update profile."
      );
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <p>Loading profile...</p>;
  }

  return (
    <div className="profile-setup">

      <h2>My Profile</h2>

      <p>Update your career preferences and technical skills.</p>
<ProfileImage />
      <form onSubmit={handleSubmit}>

        <div className="form-group">
          <label htmlFor="profileName">Full Name</label>

          <input
            id="profileName"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter your full name"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="targetRole">Target Job Role</label>

          <input
            id="targetRole"
            type="text"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            placeholder="e.g. Python Developer"
          />
        </div>

        <div className="form-group">
          <label htmlFor="skills">Technical Skills</label>

          <input
            id="skills"
            type="text"
            value={skills}
            onChange={(e) => setSkills(e.target.value)}
            placeholder="Python, React, FastAPI, MongoDB"
          />

          <small>Separate multiple skills using commas.</small>
        </div>

        {error && (
          <p className="error-message">{error}</p>
        )}

        {success && (
          <p className="success-message">{success}</p>
        )}

        <button type="submit" disabled={saving}>
          {saving ? "Saving..." : "Save Profile"}
        </button>

      </form>

    </div>
  );
}

export default ProfileSetup;
