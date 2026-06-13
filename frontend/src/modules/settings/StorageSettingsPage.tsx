import { IntegrationSettingsForm } from "./IntegrationSettingsForm";

export function StorageSettingsPage() {
  return (
    <IntegrationSettingsForm
      title="Storage Settings"
      description="Configure tenant storage credentials for future Google Cloud Storage or AWS S3 use."
      providers={["GOOGLE_CLOUD_STORAGE", "AWS_S3"]}
    />
  );
}
