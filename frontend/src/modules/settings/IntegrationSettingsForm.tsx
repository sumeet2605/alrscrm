import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { App, Button, Card, Form, Input, Select, Space, Tag, Typography } from "antd";

import { createIntegration, listIntegrations, updateIntegration } from "../../api/integrations";
import { useAuth } from "../../contexts/AuthContext";
import type { IntegrationProvider } from "../../types/integrations";
import { labelFromEnum, providerFields, statusColor } from "./integrationOptions";

interface IntegrationSettingsFormProps {
  title: string;
  description: string;
  providers: IntegrationProvider[];
}

export function IntegrationSettingsForm({
  title,
  description,
  providers
}: IntegrationSettingsFormProps) {
  const { user } = useAuth();
  const { message } = App.useApp();
  const queryClient = useQueryClient();
  const [form] = Form.useForm();
  const selectedProvider = Form.useWatch("provider", form) as IntegrationProvider | undefined;
  const provider = selectedProvider ?? providers[0];
  const integrationsQuery = useQuery({
    queryKey: ["integrations", provider],
    queryFn: () => listIntegrations({ page: 1, page_size: 1, provider }),
    enabled: Boolean(provider)
  });
  const existing = integrationsQuery.data?.items[0];
  const saveMutation = useMutation({
    mutationFn: async (values: Record<string, string>) => {
      const credentials = Object.fromEntries(
        providerFields(provider).map((field) => [field, values[field]])
      );
      if (existing) {
        return updateIntegration(existing.id, { credentials });
      }
      return createIntegration({
        organization_id: user!.organization_id,
        branch_id: user?.branch_id ?? undefined,
        provider,
        credentials
      });
    },
    onSuccess: async () => {
      message.success("Integration settings saved");
      form.resetFields();
      await queryClient.invalidateQueries({ queryKey: ["integrations"] });
      await queryClient.invalidateQueries({ queryKey: ["integration-health"] });
    }
  });

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>{title}</Typography.Title>
          <Typography.Text type="secondary">{description}</Typography.Text>
        </div>
      </div>

      <Card
        title={
          <Space>
            <span>{labelFromEnum(provider)}</span>
            {existing ? (
              <Tag color={statusColor(existing.status)}>{labelFromEnum(existing.status)}</Tag>
            ) : null}
          </Space>
        }
        loading={integrationsQuery.isLoading}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{ provider }}
          onFinish={(values) => saveMutation.mutate(values)}
        >
          <Form.Item name="provider" label="Provider" rules={[{ required: true }]}>
            <Select
              options={providers.map((item) => ({ value: item, label: labelFromEnum(item) }))}
            />
          </Form.Item>
          {providerFields(provider).map((field) => (
            <Form.Item
              key={field}
              name={field}
              label={labelFromEnum(field)}
              rules={[{ required: true }]}
            >
              {field.includes("json") ? <Input.TextArea rows={5} /> : <Input.Password />}
            </Form.Item>
          ))}
          <Button type="primary" htmlType="submit" loading={saveMutation.isPending}>
            Save Settings
          </Button>
        </Form>
      </Card>
    </Space>
  );
}
