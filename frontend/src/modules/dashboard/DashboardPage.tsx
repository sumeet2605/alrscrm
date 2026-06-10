import {
  ApartmentOutlined,
  CheckCircleOutlined,
  DollarOutlined,
  PercentageOutlined,
  TeamOutlined
} from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { Card, Col, Row, Space, Statistic, Table, Tag, Typography } from "antd";

import { listBranches, listUsers } from "../../api/identity";
import { getSalesMetrics } from "../../api/sales";
import { useAuth } from "../../contexts/AuthContext";

const activity = [
  { key: "1", event: "Super admin seed verified", actor: "System", status: "Complete" },
  { key: "2", event: "RBAC baseline loaded", actor: "System", status: "Complete" },
  { key: "3", event: "Identity API available", actor: "API", status: "Healthy" }
];

export function DashboardPage() {
  const { user } = useAuth();
  const usersQuery = useQuery({
    queryKey: ["dashboard", "users"],
    queryFn: () => listUsers({ page: 1, page_size: 1 })
  });
  const branchesQuery = useQuery({
    queryKey: ["dashboard", "branches"],
    queryFn: () => listBranches({ page: 1, page_size: 1 })
  });
  const salesMetricsQuery = useQuery({
    queryKey: ["dashboard", "sales-metrics"],
    queryFn: getSalesMetrics
  });

  return (
    <Space direction="vertical" size={20} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Dashboard</Typography.Title>
          <Typography.Text type="secondary">
            Welcome back, {user?.first_name}. Identity operations are ready.
          </Typography.Text>
        </div>
      </div>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Average Opportunity Value"
              value={salesMetricsQuery.data?.average_opportunity_value ?? 0}
              loading={salesMetricsQuery.isLoading}
              prefix="₹"
              precision={0}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Booked Opportunities"
              value={salesMetricsQuery.data?.booked_opportunities ?? 0}
              loading={salesMetricsQuery.isLoading}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Users"
              value={usersQuery.data?.meta.total ?? 0}
              loading={usersQuery.isLoading}
              prefix={<TeamOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Branches"
              value={branchesQuery.data?.meta.total ?? 0}
              loading={branchesQuery.isLoading}
              prefix={<ApartmentOutlined />}
            />
          </Card>
        </Col>
      </Row>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Open Opportunities"
              value={salesMetricsQuery.data?.open_opportunities ?? 0}
              loading={salesMetricsQuery.isLoading}
              prefix={<DollarOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Lost Opportunities"
              value={salesMetricsQuery.data?.lost_opportunities ?? 0}
              loading={salesMetricsQuery.isLoading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Conversion Rate"
              value={salesMetricsQuery.data?.conversion_rate ?? 0}
              suffix="%"
              loading={salesMetricsQuery.isLoading}
              prefix={<PercentageOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Missed Follow Ups"
              value={salesMetricsQuery.data?.missed_followups ?? 0}
              loading={salesMetricsQuery.isLoading}
            />
          </Card>
        </Col>
      </Row>
      <Row gutter={[16, 16]}>
        <Col xs={24} xl={16}>
          <Card title="Recent Activity">
            <Table
              pagination={false}
              dataSource={activity}
              columns={[
                { title: "Event", dataIndex: "event" },
                { title: "Actor", dataIndex: "actor", width: 160 },
                {
                  title: "Status",
                  dataIndex: "status",
                  width: 140,
                  render: (status) => <Tag color="green">{status}</Tag>
                }
              ]}
            />
          </Card>
        </Col>
        <Col xs={24} xl={8}>
          <Card title="System Status">
            <Space direction="vertical" size={14}>
              <StatusItem label="API" value="Online" />
              <StatusItem label="Database" value="Healthy" />
              <StatusItem label="RBAC" value="Seeded" />
            </Space>
          </Card>
        </Col>
      </Row>
    </Space>
  );
}

function StatusItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="status-row">
      <Typography.Text>{label}</Typography.Text>
      <Tag color="success">{value}</Tag>
    </div>
  );
}
