
import DashboardAnalytics from "../features/dashboard/DashboardAnalytics";

function Dashboard() {
  return (
    <div className="dashboard-overview">

      <section className="welcome-section">
        <h2>Dashboard Overview</h2>

        <p>
          Welcome to your AI-powered interview preparation platform.
        </p>

        <p>
          Manage your profile, analyze resumes, practice interviews
          and track your career development from one place.
        </p>
      </section>

      <section className="dashboard-analytics-section">
        <DashboardAnalytics />
      </section>

      <section className="overview-info">
        <h2>Get Started</h2>

        <p>
          Select any option from the sidebar to access your profile,
          resumes, interviews or personalized career roadmap.
        </p>
      </section>

    </div>
  );
}

export default Dashboard;
