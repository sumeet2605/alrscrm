import { CheckCircleOutlined, CloseCircleOutlined, ExclamationCircleOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { App, Button, Card, Col, Row, Select, Space, Statistic, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import dayjs from "dayjs";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { getIntegrationHealth, listIntegrations, verifyIntegration } from "../../api/integrations";
import type { Integration, IntegrationProvider, IntegrationStatus } from "../../types/integrations";
import {
  integrationProviders,
  integrationStatuses,
  labelFromEnum,
  statusColor
} from "./integrationOptions";

export function IntegrationsDashboardPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { message } = App.useApp();
  const [provider, setProvider] = useState<IntegrationProvider | undefined>();
  const [status, setStatus] = useState<IntegrationStatus | undefined>();
  const healthQuery = useQuery({
    queryKey: ["integration-health"],
    queryFn: getIntegrationHealth
  });
  const integrationsQuery = useQuery({
    queryKey: ["integrations", provider, status],
    queryFn: () => listIntegrations({ page: 1, page_size: 50, provider, status })
  });
  const verifyMutation = useMutation({
    mutationFn: verifyIntegration,
    onSuccess: async () => {
      message.success("Integration verified");
      await queryClient.invalidateQueries({ queryKey: ["integrations"] });
      await queryClient.invalidateQueries({ queryKey: ["integration-health"] });
    }
  });
  const health = healthQuery.data;
  const columns: ColumnsType<Integration> = [
    { title: "Provider", dataIndex: "provider", render: (value) => labelFromEnum(value) },
    {
      title: "Status",
      dataIndex: "status",
      render: (value: IntegrationStatus) => (
        <Tag color={statusColor(value)}>{labelFromEnum(value)}</Tag>
      )
    },
    {
      title: "Credential Keys",
      dataIndex: "credential_keys",
      render: (keys: string[]) => keys.join(", ")
    },
    {
      title: "Last Verified",
      dataIndex: "last_verified_at",
      render: (value?: string | null) => (value ? dayjs(value).format("DD MMM YYYY HH:mm") : "-")
    },
    {
      title: "Actions",
      render: (_, item) => (
        <Space>
          <Button onClick={() => verifyMutation.mutate(item.id)}>Verify</Button>
        </Space>
      )
    }
  ];

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Integrations</Typography.Title>
          <Typography.Text type="secondary">
            Manage tenant-owned provider credentials and operational connection health.
          </Typography.Text>
        </div>
        <Space wrap>
          <Button onClick={() => navigate("/settings/integrations/whatsapp")}>WhatsApp</Button>
          <Button onClick={() => navigate("/settings/integrations/email")}>Email</Button>
          <Button onClick={() => navigate("/settings/integrations/storage")}>Storage</Button>
        </Space>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Connected"
              value={health?.connected ?? 0}
              loading={healthQuery.isLoading}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Disconnected"
              value={health?.disconnected ?? 0}
              loading={healthQuery.isLoading}
              prefix={<CloseCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Expired"
              value={health?.expired ?? 0}
              loading={healthQuery.isLoading}
              prefix={<ExclamationCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Error"
              value={health?.error ?? 0}
              loading={healthQuery.isLoading}
              prefix={<ExclamationCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Space wrap>
        <Select
          allowClear
          placeholder="Provider"
          className="filter-control"
          value={provider}
          options={integrationProviders.map((item) => ({ value: item, label: labelFromEnum(item) }))}
          onChange={setProvider}
        />
        <Select
          allowClear
          placeholder="Status"
          className="filter-control"
          value={status}
          options={integrationStatuses.map((item) => ({ value: item, label: labelFromEnum(item) }))}
          onChange={setStatus}
        />
      </Space>

      <Table<Integration>
        rowKey="id"
        loading={integrationsQuery.isLoading}
        dataSource={integrationsQuery.data?.items ?? []}
        columns={columns}
      />
    </Space>
  );
}
