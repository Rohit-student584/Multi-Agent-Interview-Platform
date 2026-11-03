
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useParams,
} from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import ProfileView from "./features/auth/ProfileView";
import DashboardLayout from "./layouts/DashboardLayout";

import ProfileSetup from "./features/auth/ProfileSetup";
import ResumeUpload from "./features/resume/ResumeUpload";
import ResumeList from "./features/resume/ResumeList";

import InterviewSetup from "./features/interview/InterviewSetup";
import InterviewHistory from "./features/interview/InterviewHistory";
import InterviewSession from "./features/interview/InterviewSession";

import RoadmapGenerator from "./features/roadmap/RoadmapGenerator";

import InterviewResults from "./pages/InterviewResults";


function InterviewPage() {
  const { interviewId } = useParams();

  return <InterviewSession interviewId={interviewId} />;
}


function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Authentication Routes */}

        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />


        {/* Dashboard Layout with Sidebar */}

        <Route path="/dashboard" element={<DashboardLayout />}>

          <Route index element={<Dashboard />} />

        <Route
  path="profile"
  element={<ProfileView />}
/>

<Route
  path="profile/edit"
  element={<ProfileSetup />}
/>
          <Route
            path="resume-upload"
            element={<ResumeUpload />}
          />

          <Route
            path="resumes"
            element={<ResumeList />}
          />

          <Route
            path="interview-setup"
            element={<InterviewSetup />}
          />

          <Route
            path="interview-history"
            element={<InterviewHistory />}
          />

          <Route
            path="roadmap"
            element={<RoadmapGenerator />}
          />

        </Route>


        {/* Interview Routes */}

        <Route
          path="/interview/:interviewId"
          element={<InterviewPage />}
        />

        <Route
          path="/interview/:interviewId/results"
          element={<InterviewResults />}
        />


        {/* Default Route */}

        <Route
          path="*"
          element={<Navigate to="/login" replace />}
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;
