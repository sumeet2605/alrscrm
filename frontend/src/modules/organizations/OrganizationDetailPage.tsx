import { ArrowLeftOutlined, SaveOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { App, Button, Form, Input, Space, Spin, Switch, Tabs, Typography } from "antd";
import { useEffect } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";

import {
  getOrganization,
  getOrganizationSettings,
  updateOrganization,
  updateOrganizationSettings
} from "../../api/identity";
import type {
  OrganizationSettingsUpdatePayload,
  OrganizationUpdatePayload
} from "../../types/identity";

export function OrganizationDetailPage() {
  const { organizationId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { message } = App.useApp();
  const queryClient = useQueryClient();
  const [organizationForm] = Form.useForm<OrganizationUpdatePayload>();
  const [settingsForm] = Form.useForm<OrganizationSettingsUpdatePayload>();

  const organizationQuery = useQuery({
    queryKey: ["organization", organizationId],
    queryFn: () => getOrganization(organizationId!),
    enabled: Boolean(organizationId)
  });
  const settingsQuery = useQuery({
    queryKey: ["organization-settings", organizationId],
    queryFn: () => getOrganizationSettings(organizationId!),
    enabled: Boolean(organizationId)
  });

  useEffect(() => {
    if (organizationQuery.data) {
      organizationForm.setFieldsValue(organizationQuery.data);
    }
  }, [organizationForm, organizationQuery.data]);

  useEffect(() => {
    if (settingsQuery.data) {
      settingsForm.setFieldsValue(settingsQuery.data);
    }
  }, [settingsForm, settingsQuery.data]);

  const updateOrgMutation = useMutation({
    mutationFn: (payload: OrganizationUpdatePayload) => updateOrganization(organizationId!, payload),
    onSuccess: async () => {
      message.success("Organization updated");
      await queryClient.invalidateQueries({ queryKey: ["organization", organizationId] });
      await queryClient.invalidateQueries({ queryKey: ["organizations"] });
    }
  });

  const updateSettingsMutation = useMutation({
    mutationFn: (payload: OrganizationSettingsUpdatePayload) =>
      updateOrganizationSettings(organizationId!, payload),
    onSuccess: async () => {
      message.success("Organization settings updated");
      await queryClient.invalidateQueries({ queryKey: ["organization-settings", organizationId] });
    }
  });

  if (organizationQuery.isLoading || settingsQuery.isLoading) {
    return <Spin />;
  }

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>{organizationQuery.data?.name ?? "Organization"}</Typography.Title>
          <Typography.Text type="secondary">Review tenant details and settings.</Typography.Text>
        </div>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/organizations")}>
          Back
        </Button>
      </div>
      <Tabs
        activeKey={location.pathname.endsWith("/settings") ? "settings" : "details"}
        onChange={(key) => {
          navigate(key === "settings" ? `/organizations/${organizationId}/settings` : `/organizations/${organizationId}`);
        }}
        items={[
          {
            key: "details",
            label: "Details",
            children: (
              <Form
                form={organizationForm}
                layout="vertical"
                requiredMark={false}
                onFinish={(values) => updateOrgMutation.mutate(values)}
              >
                <Form.Item label="Name" name="name" rules={[{ required: true }]}>
                  <Input />
                </Form.Item>
                <Form.Item label="Code" name="code" rules={[{ required: true }]}>
                  <Input />
                </Form.Item>
                <Form.Item label="Active" name="is_active" valuePropName="checked">
                  <Switch />
                </Form.Item>
                <Button
                  type="primary"
                  icon={<SaveOutlined />}
                  loading={updateOrgMutation.isPending}
                  onClick={() => organizationForm.submit()}
                >
                  Save Details
                </Button>
              </Form>
            )
          },
          {
            key: "settings",
            label: "Settings",
            children: (
              <Form
                form={settingsForm}
                layout="vertical"
                requiredMark={false}
                onFinish={(values) => updateSettingsMutation.mutate(values)}
              >
                <Form.Item label="Studio Name" name="studio_name" rules={[{ required: true }]}>
                  <Input />
                </Form.Item>
                <Form.Item label="Logo URL" name="logo_url">
                  <Input />
                </Form.Item>
                <Form.Item label="Contact Email" name="contact_email" rules={[{ type: "email" }]}>
                  <Input />
                </Form.Item>
                <Form.Item label="Contact Phone" name="contact_phone">
                  <Input />
                </Form.Item>
                <Form.Item label="Website" name="website">
                  <Input />
                </Form.Item>
                <Form.Item label="Address" name="address">
                  <Input.TextArea rows={3} />
                </Form.Item>
                <Form.Item label="Timezone" name="timezone" rules={[{ required: true }]}>
                  <Input />
                </Form.Item>
                <Form.Item label="Currency" name="currency" rules={[{ required: true, len: 3 }]}>
                  <Input />
                </Form.Item>
                <Form.Item
                  label="Delivery Expiry Default"
                  name="delivery_expiry_default"
                  rules={[{ required: true }]}
                >
                  <Input type="number" />
                </Form.Item>
                <Form.Item
                  label="Gallery Selection Default Limit"
                  name="gallery_selection_default_limit"
                  rules={[{ required: true }]}
                >
                  <Input type="number" />
                </Form.Item>
                <Button
                  type="primary"
                  icon={<SaveOutlined />}
                  loading={updateSettingsMutation.isPending}
                  onClick={() => settingsForm.submit()}
                >
                  Save Settings
                </Button>
              </Form>
            )
          }
        ]}
      />
    </Space>
  );
}
