
import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { UserRound, BriefcaseBusiness, Code, Mail, Pencil } from "lucide-react";
import ProfileImage from "./ProfileImage";
import "../../styles/ProfileView.css";
import api from "../../api/axios";
import { useAuth } from "./AuthContext";

function ProfileView() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchProfile = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/api/users/me");

      setProfile(response.data);

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Failed to load profile."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  if (loading) {
    return <p>Loading your profile...</p>;
  }

  if (error) {
    return (
      <div className="profile-view">
        <p className="error-message">{error}</p>
        <button onClick={fetchProfile}>Retry</button>
      </div>
    );
  }

  if (!profile) {
    return <p>No profile information found.</p>;
  }

  const skills = profile.skills || [];

  return (
    <div className="profile-view">

      <div className="profile-view-header">
        <div>
          <h2>My Profile</h2>
          <p>View your personal and professional information.</p>
        </div>

        <button
          className="edit-profile-btn"
          onClick={() => navigate("/dashboard/profile/edit")}
        >
          <Pencil size={17} />
          Edit Profile
        </button>
      </div>

      <div className="profile-view-card">

     <ProfileImage />

        <h2>{profile.name || "Name not available"}</h2>

        <p className="profile-view-email">
          {user?.email || profile.email || "Email not available"}
        </p>

        <div className="profile-details">

          <div className="profile-detail-item">
            <Mail size={20} />

            <div>
              <span>Email Address</span>
              <strong>
                {user?.email || profile.email || "Not available"}
              </strong>
            </div>
          </div>

          <div className="profile-detail-item">
            <BriefcaseBusiness size={20} />

            <div>
              <span>Target Job Role</span>
              <strong>
                {profile.target_role || "Not specified"}
              </strong>
            </div>
          </div>

          <div className="profile-detail-item skills-detail">
            <Code size={20} />

            <div>
              <span>Technical Skills</span>

              {skills.length > 0 ? (
                <div className="profile-skills">
                  {skills.map((skill, index) => (
                    <span className="skill-tag" key={index}>
                      {skill}
                    </span>
                  ))}
                </div>
              ) : (
                <strong>No skills added yet.</strong>
              )}
            </div>
          </div>

        </div>

        <button
          className="edit-profile-bottom-btn"
          onClick={() => navigate("/dashboard/profile/edit")}
        >
          Edit My Profile
        </button>

      </div>

    </div>
  );
}

export default ProfileView;
