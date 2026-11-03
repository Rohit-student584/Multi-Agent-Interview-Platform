
import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth } from "firebase/auth";


// Firebase configuration from frontend .env
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

// Initialize Firebase only once
const app = getApps().length
  ? getApp()
  : initializeApp(firebaseConfig);

// Initialize Firebase Authentication
export const auth = getAuth(app);

// Initialize Firebase Storage


export default app;
