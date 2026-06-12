import { Navigate, Route, Routes } from "react-router-dom";

import { DashboardLayout } from "../layouts/DashboardLayout";
import { AssignmentBoardPage } from "../modules/bookings/AssignmentBoardPage";
import { BookingCreatePage } from "../modules/bookings/BookingCreatePage";
import { BookingDetailsPage } from "../modules/bookings/BookingDetailsPage";
import { BookingListPage } from "../modules/bookings/BookingListPage";
import { ClientSelectionPage } from "../modules/bookings/ClientSelectionPage";
import { GalleryDetailsPage } from "../modules/bookings/GalleryDetailsPage";
import { GalleryManagementPage } from "../modules/bookings/GalleryManagementPage";
import { GalleryUploadPage } from "../modules/bookings/GalleryUploadPage";
import { PackageManagementPage } from "../modules/bookings/PackageManagementPage";
import { ScheduleCalendarPage } from "../modules/bookings/ScheduleCalendarPage";
import { BranchManagementPage } from "../modules/branches/BranchManagementPage";
import { DashboardPage } from "../modules/dashboard/DashboardPage";
import { ClientDeliveryPage } from "../modules/delivery/ClientDeliveryPage";
import { DeliveryDashboardPage } from "../modules/delivery/DeliveryDashboardPage";
import { DeliveryDetailPage } from "../modules/delivery/DeliveryDetailPage";
import { DeliveryQueuePage } from "../modules/delivery/DeliveryQueuePage";
import { FamilyDetailsPage } from "../modules/families/FamilyDetailsPage";
import { FamilyFormPage } from "../modules/families/FamilyFormPage";
import { FamilyListPage } from "../modules/families/FamilyListPage";
import { FinanceDashboardPage } from "../modules/finance/FinanceDashboardPage";
import { InvoiceDetailPage } from "../modules/finance/InvoiceDetailPage";
import { InvoiceListPage } from "../modules/finance/InvoiceListPage";
import { PaymentDetailPage } from "../modules/finance/PaymentDetailPage";
import { PaymentListPage } from "../modules/finance/PaymentListPage";
import { OrganizationDetailPage } from "../modules/organizations/OrganizationDetailPage";
import { OrganizationListPage } from "../modules/organizations/OrganizationListPage";
import { OrganizationOnboardingPage } from "../modules/organizations/OrganizationOnboardingPage";
import { EditingJobDetailPage } from "../modules/production/EditingJobDetailPage";
import { EditingQueuePage } from "../modules/production/EditingQueuePage";
import { EditorDashboardPage } from "../modules/production/EditorDashboardPage";
import { ProductionDashboardPage } from "../modules/production/ProductionDashboardPage";
import { RoleManagementPage } from "../modules/roles/RoleManagementPage";
import { OpportunityDetailsPage } from "../modules/sales/OpportunityDetailsPage";
import { OpportunityFormPage } from "../modules/sales/OpportunityFormPage";
import { OpportunityListPage } from "../modules/sales/OpportunityListPage";
import { SalesDashboardPage } from "../modules/sales/SalesDashboardPage";
import { EmailSettingsPage } from "../modules/settings/EmailSettingsPage";
import { IntegrationsDashboardPage } from "../modules/settings/IntegrationsDashboardPage";
import { StorageSettingsPage } from "../modules/settings/StorageSettingsPage";
import { WhatsAppSettingsPage } from "../modules/settings/WhatsAppSettingsPage";
import { UserManagementPage } from "../modules/users/UserManagementPage";
import { ChangePasswordPage } from "../pages/ChangePasswordPage";
import { LoginPage } from "../pages/LoginPage";
import { ProtectedRoute } from "./ProtectedRoute";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/client/gallery/:token" element={<ClientSelectionPage />} />
      <Route path="/client/delivery/:token" element={<ClientDeliveryPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/change-password" element={<ChangePasswordPage />} />
        <Route element={<DashboardLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/organizations" element={<OrganizationListPage />} />
          <Route path="/organizations/new" element={<OrganizationOnboardingPage />} />
          <Route path="/organizations/:organizationId" element={<OrganizationDetailPage />} />
          <Route path="/organizations/:organizationId/settings" element={<OrganizationDetailPage />} />
          <Route path="/families" element={<FamilyListPage />} />
          <Route path="/families/new" element={<FamilyFormPage />} />
          <Route path="/families/:familyId" element={<FamilyDetailsPage />} />
          <Route path="/families/:familyId/edit" element={<FamilyFormPage />} />
          <Route path="/sales" element={<SalesDashboardPage />} />
          <Route path="/sales/opportunities" element={<OpportunityListPage />} />
          <Route path="/sales/opportunities/new" element={<OpportunityFormPage />} />
          <Route path="/sales/opportunities/:opportunityId" element={<OpportunityDetailsPage />} />
          <Route path="/bookings" element={<BookingListPage />} />
          <Route path="/bookings/new" element={<BookingCreatePage />} />
          <Route path="/bookings/:bookingId" element={<BookingDetailsPage />} />
          <Route path="/packages" element={<PackageManagementPage />} />
          <Route path="/galleries" element={<GalleryManagementPage />} />
          <Route path="/galleries/:galleryId" element={<GalleryDetailsPage />} />
          <Route path="/galleries/:galleryId/upload" element={<GalleryUploadPage />} />
          <Route path="/production" element={<ProductionDashboardPage />} />
          <Route path="/production/editing" element={<EditingQueuePage />} />
          <Route path="/production/editing/:jobId" element={<EditingJobDetailPage />} />
          <Route path="/production/editor-dashboard" element={<EditorDashboardPage />} />
          <Route path="/delivery" element={<DeliveryQueuePage />} />
          <Route path="/delivery/dashboard" element={<DeliveryDashboardPage />} />
          <Route path="/delivery/:deliveryId" element={<DeliveryDetailPage />} />
          <Route path="/finance" element={<FinanceDashboardPage />} />
          <Route path="/finance/invoices" element={<InvoiceListPage />} />
          <Route path="/finance/invoices/:invoiceId" element={<InvoiceDetailPage />} />
          <Route path="/finance/payments" element={<PaymentListPage />} />
          <Route path="/finance/payments/:paymentId" element={<PaymentDetailPage />} />
          <Route path="/settings/integrations" element={<IntegrationsDashboardPage />} />
          <Route path="/settings/integrations/whatsapp" element={<WhatsAppSettingsPage />} />
          <Route path="/settings/integrations/email" element={<EmailSettingsPage />} />
          <Route path="/settings/integrations/storage" element={<StorageSettingsPage />} />
          <Route path="/schedules" element={<ScheduleCalendarPage />} />
          <Route path="/schedules/assignments" element={<AssignmentBoardPage />} />
          <Route path="/branches" element={<BranchManagementPage />} />
          <Route path="/users" element={<UserManagementPage />} />
          <Route path="/roles" element={<RoleManagementPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
