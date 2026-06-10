import { QueryClientProvider } from "@tanstack/react-query";
import { ConfigProvider } from "antd";
import { BrowserRouter } from "react-router-dom";

import { ErrorBoundary } from "../components/ErrorBoundary";
import { AuthProvider } from "../contexts/AuthContext";
import { AppRoutes } from "../routes/AppRoutes";
import { appTheme } from "../theme/theme";
import { queryClient } from "./queryClient";

export function App() {
  return (
    <ConfigProvider theme={appTheme}>
      <ErrorBoundary>
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <AuthProvider>
              <AppRoutes />
            </AuthProvider>
          </BrowserRouter>
        </QueryClientProvider>
      </ErrorBoundary>
    </ConfigProvider>
  );
}
