import { IntegrationSettingsForm } from "./IntegrationSettingsForm";

export function EmailSettingsPage() {
  return (
    <IntegrationSettingsForm
      title="Email Settings"
      description="Configure SMTP credentials for future tenant email delivery."
      providers={["SMTP_EMAIL"]}
    />
  );
}
