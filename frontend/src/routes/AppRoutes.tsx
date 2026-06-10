import { Navigate, Route, Routes } from "react-router-dom";

import { DashboardLayout } from "../layouts/DashboardLayout";
import { BranchManagementPage } from "../modules/branches/BranchManagementPage";
import { DashboardPage } from "../modules/dashboard/DashboardPage";
import { FamilyDetailsPage } from "../modules/families/FamilyDetailsPage";
import { FamilyFormPage } from "../modules/families/FamilyFormPage";
import { FamilyListPage } from "../modules/families/FamilyListPage";
import { RoleManagementPage } from "../modules/roles/RoleManagementPage";
import { OpportunityDetailsPage } from "../modules/sales/OpportunityDetailsPage";
import { OpportunityFormPage } from "../modules/sales/OpportunityFormPage";
import { OpportunityListPage } from "../modules/sales/OpportunityListPage";
import { SalesDashboardPage } from "../modules/sales/SalesDashboardPage";
import { UserManagementPage } from "../modules/users/UserManagementPage";
import { LoginPage } from "../pages/LoginPage";
import { ProtectedRoute } from "./ProtectedRoute";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<DashboardLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/families" element={<FamilyListPage />} />
          <Route path="/families/new" element={<FamilyFormPage />} />
          <Route path="/families/:familyId" element={<FamilyDetailsPage />} />
          <Route path="/families/:familyId/edit" element={<FamilyFormPage />} />
          <Route path="/sales" element={<SalesDashboardPage />} />
          <Route path="/sales/opportunities" element={<OpportunityListPage />} />
          <Route path="/sales/opportunities/new" element={<OpportunityFormPage />} />
          <Route path="/sales/opportunities/:opportunityId" element={<OpportunityDetailsPage />} />
          <Route path="/branches" element={<BranchManagementPage />} />
          <Route path="/users" element={<UserManagementPage />} />
          <Route path="/roles" element={<RoleManagementPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
