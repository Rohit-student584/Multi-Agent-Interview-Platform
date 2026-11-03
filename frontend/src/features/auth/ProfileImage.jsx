
import { useCallback, useEffect, useRef, useState } from "react";
import { UserRound, Upload, Trash2 } from "lucide-react";
import "../../styles/ProfileImage.css";
import api from "../../api/axios";

function ProfileImage() {
  const [imageUrl, setImageUrl] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const [imageLoading, setImageLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const fileInputRef = useRef(null);
  const imageUrlRef = useRef(null);
  const previewUrlRef = useRef(null);

  // Fetch existing profile image
  const fetchProfileImage = useCallback(async () => {
    setImageLoading(true);

    try {
      const response = await api.get(
        "/api/users/me/profile-image",
        {
          responseType: "blob",
        }
      );

      const objectUrl = URL.createObjectURL(response.data);

      if (imageUrlRef.current) {
        URL.revokeObjectURL(imageUrlRef.current);
      }

      imageUrlRef.current = objectUrl;
      setImageUrl(objectUrl);

    } catch (err) {
      if (err.response?.status !== 404) {
        setError(
          err.response?.data?.detail ||
          "Failed to load profile image."
        );
      }

      setImageUrl(null);

    } finally {
      setImageLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProfileImage();

    return () => {
      if (imageUrlRef.current) {
        URL.revokeObjectURL(imageUrlRef.current);
      }

      if (previewUrlRef.current) {
        URL.revokeObjectURL(previewUrlRef.current);
      }
    };
  }, [fetchProfileImage]);

  // Select and validate image
  const handleImageChange = (e) => {
    const file = e.target.files?.[0];

    setError("");
    setSuccess("");

    if (!file) return;

    const allowedTypes = [
      "image/jpeg",
      "image/png",
      "image/webp",
    ];

    if (!allowedTypes.includes(file.type)) {
      setError("Only JPG, PNG and WEBP images are supported.");
      e.target.value = "";
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setError("Image size must not exceed 5 MB.");
      e.target.value = "";
      return;
    }

    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current);
    }

    const objectUrl = URL.createObjectURL(file);

    previewUrlRef.current = objectUrl;

    setPreviewUrl(objectUrl);
    setSelectedFile(file);
  };

  // Upload or replace profile image
  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select an image first.");
      return;
    }

    setUploading(true);
    setError("");
    setSuccess("");

    try {
      const formData = new FormData();

      formData.append("file", selectedFile);

      await api.post(
        "/api/users/me/profile-image",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      if (previewUrlRef.current) {
        URL.revokeObjectURL(previewUrlRef.current);
        previewUrlRef.current = null;
      }

      setPreviewUrl(null);
      setSelectedFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      await fetchProfileImage();

      setSuccess("Profile picture updated successfully!");

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Profile image upload failed."
      );
    } finally {
      setUploading(false);
    }
  };

  // Delete profile image
  const handleDelete = async () => {
    if (!imageUrl && !previewUrl) return;

    if (previewUrl) {
      URL.revokeObjectURL(previewUrlRef.current);
      previewUrlRef.current = null;

      setPreviewUrl(null);
      setSelectedFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      return;
    }

    setDeleting(true);
    setError("");
    setSuccess("");

    try {
      await api.delete("/api/users/me/profile-image");

      if (imageUrlRef.current) {
        URL.revokeObjectURL(imageUrlRef.current);
        imageUrlRef.current = null;
      }

      setImageUrl(null);
      setSuccess("Profile picture removed successfully!");

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Failed to delete profile picture."
      );
    } finally {
      setDeleting(false);
    }
  };

  const displayedImage = previewUrl || imageUrl;

  return (
    <div className="profile-image-section">

      <div className="profile-image-heading">
        <h3>Profile Picture</h3>
        <p>Upload or update your profile picture.</p>
      </div>

      <div className="profile-image-preview">

        {imageLoading ? (
          <p>Loading profile picture...</p>
        ) : displayedImage ? (
          <img
            src={displayedImage}
            alt="Profile"
            className="profile-image"
          />
        ) : (
          <div className="default-profile-avatar">
            <UserRound size={60} />
          </div>
        )}

        {previewUrl && (
          <span className="image-preview-label">
            Preview
          </span>
        )}

      </div>

      <p className="profile-image-hint">
        Supported formats: JPG, PNG, WEBP. Maximum size: 5 MB.
      </p>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={handleImageChange}
        disabled={uploading || deleting || imageLoading}
      />

      {error && (
        <p className="error-message">{error}</p>
      )}

      {success && (
        <p className="success-message">{success}</p>
      )}

      <div className="profile-image-actions">

        <button
          type="button"
          className="upload-image-btn"
          onClick={handleUpload}
          disabled={!selectedFile || uploading || deleting}
        >
          <Upload size={17} />

          {uploading
            ? "Uploading..."
            : "Save Profile Picture"}
        </button>

        {(imageUrl || previewUrl) && (
          <button
            type="button"
            className="delete-image-btn"
            onClick={handleDelete}
            disabled={uploading || deleting}
          >
            <Trash2 size={17} />

            {deleting ? "Removing..." : "Remove Picture"}
          </button>
        )}

      </div>

    </div>
  );
}

export default ProfileImage;
