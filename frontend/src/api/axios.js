
import axios from "axios";
import { auth } from "../utils/firebase";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 180000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Wait for Firebase authentication and attach ID token
api.interceptors.request.use(
  async (config) => {
    // Wait until Firebase restores the initial auth state
    await auth.authStateReady();

    const user = auth.currentUser;

    if (!user) {
      throw new Error(
        "Authentication required. Please login first."
      );
    }

    // Get a valid Firebase ID token
    const idToken = await user.getIdToken();

    config.headers.Authorization = `Bearer ${idToken}`;

    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
