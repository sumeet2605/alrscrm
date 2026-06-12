import { IntegrationSettingsForm } from "./IntegrationSettingsForm";

export function WhatsAppSettingsPage() {
  return (
    <IntegrationSettingsForm
      title="WhatsApp Settings"
      description="Configure WhatsApp Cloud API credentials for future tenant messaging workflows."
      providers={["WHATSAPP_CLOUD_API", "INSTAGRAM_BUSINESS", "FACEBOOK_PAGE"]}
    />
  );
}
