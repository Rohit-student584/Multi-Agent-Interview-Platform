import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
} from "firebase/auth";

import { auth } from "../../utils/firebase";

const AuthContext = createContext(null);

// Authentication Provider
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Register new user
  const register = (email, password) => {
    return createUserWithEmailAndPassword(
      auth,
      email,
      password
    );
  };

  // Login existing user
  const login = (email, password) => {
    return signInWithEmailAndPassword(
      auth,
      email,
      password
    );
  };

  // Logout user
  const logout = () => {
    return signOut(auth);
  };

  // Track authentication state
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(
      auth,
      (currentUser) => {
        setUser(currentUser);
        setLoading(false);
      }
    );

    return unsubscribe;
  }, []);

  const value = {
    user,
    loading,
    register,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom authentication hook
export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }

  return context;
}