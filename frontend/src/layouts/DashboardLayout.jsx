
import { useEffect, useState } from "react";
import {
  NavLink,
  Outlet,
  useNavigate,
} from "react-router-dom";

import {
  LayoutDashboard,
  UserRound,
  FileUp,
  Files,
  ClipboardList,
  History,
  Map,
  LogOut,
  Menu,
  X,
} from "lucide-react";

import { useAuth } from "../features/auth/AuthContext";
import "../styles/DashboardLayout.css";

function DashboardLayout() {
  const { user, loading, logout } = useAuth();
  const navigate = useNavigate();

  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      navigate("/login", { replace: true });
    }
  }, [user, loading, navigate]);

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/login", { replace: true });
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  if (loading) {
    return <p>Loading dashboard...</p>;
  }

  if (!user) {
    return null;
  }

  const menuItems = [
    {
      title: "Overview",
      path: "/dashboard",
      icon: LayoutDashboard,
      end: true,
    },
    {
      title: "My Profile",
      path: "/dashboard/profile",
      icon: UserRound,
    },
    {
      title: "Upload Resume",
      path: "/dashboard/resume-upload",
      icon: FileUp,
    },
    {
      title: "My Resumes",
      path: "/dashboard/resumes",
      icon: Files,
    },
    {
      title: "Start Interview",
      path: "/dashboard/interview-setup",
      icon: ClipboardList,
    },
    {
      title: "Interview History",
      path: "/dashboard/interview-history",
      icon: History,
    },
    {
      title: "Career Roadmap",
      path: "/dashboard/roadmap",
      icon: Map,
    },
  ];

  return (
    <div className="dashboard-layout">

      {/* Mobile Header */}

      <header className="mobile-header">
        <button
          className="menu-toggle"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          aria-label="Toggle navigation menu"
        >
          {sidebarOpen ? <X size={23} /> : <Menu size={23} />}
        </button>

        <h2>Interview Platform</h2>
      </header>

      {/* Sidebar */}

      <aside
        className={`dashboard-sidebar ${
          sidebarOpen ? "sidebar-open" : ""
        }`}
      >
        <div className="sidebar-brand">
          <div className="brand-icon">
            <ClipboardList size={25} />
          </div>

          <div>
            <h2>Interview AI</h2>
            <p>Preparation Platform</p>
          </div>
        </div>

        <div className="sidebar-user">
          <div className="user-avatar">
            {user.email?.charAt(0).toUpperCase() || "U"}
          </div>

          <div className="user-info">
            <strong>Welcome Back!</strong>
            <span>{user.email}</span>
          </div>
        </div>

        <nav className="sidebar-navigation">

          <p className="sidebar-heading">MAIN MENU</p>

          {menuItems.map((item) => {
            const Icon = item.icon;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.end}
                onClick={closeSidebar}
                className={({ isActive }) =>
                  `sidebar-link ${isActive ? "active" : ""}`
                }
              >
                <Icon size={19} />
                <span>{item.title}</span>
              </NavLink>
            );
          })}

        </nav>

        <div className="sidebar-bottom">
          <button
            className="sidebar-logout"
            onClick={handleLogout}
          >
            <LogOut size={19} />
            <span>Logout</span>
          </button>
        </div>

      </aside>

      {/* Mobile Overlay */}

      {sidebarOpen && (
        <button
          className="sidebar-overlay"
          onClick={closeSidebar}
          aria-label="Close sidebar"
        />
      )}

      {/* Main Content */}

      <main className="dashboard-main">
        <div className="dashboard-topbar">
          <div>
            <h1>Multi-Agent Interview Platform</h1>
            <p>AI Powered Interview Preparation</p>
          </div>

          <div className="topbar-user">
            <span>{user.email}</span>
          </div>
        </div>

        <div className="dashboard-page-content">
          <Outlet />
        </div>
      </main>

    </div>
  );
}

export default DashboardLayout;
