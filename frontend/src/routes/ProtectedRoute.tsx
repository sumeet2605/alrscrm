import { Navigate, Outlet, useLocation } from "react-router-dom";

import { LoadingScreen } from "../components/LoadingScreen";
import { useAuth } from "../contexts/AuthContext";
import { canAccessPath } from "./routePermissions";

export function ProtectedRoute() {
  const { user, isAuthenticated, isBootstrapping } = useAuth();
  const location = useLocation();

  if (isBootstrapping) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  const roleNames = user?.roles.map((role) => role.name) ?? [];
  if (!canAccessPath(roleNames, location.pathname)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}
