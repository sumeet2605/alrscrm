import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  UserSwitchOutlined
} from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { Alert, Card, Col, Row, Space, Statistic, Typography } from "antd";

import { getEditorDashboard } from "../../api/editing";

export function EditorDashboardPage() {
  const dashboardQuery = useQuery({
    queryKey: ["editing-my-work"],
    queryFn: getEditorDashboard
  });
  const dashboard = dashboardQuery.data;

  return (
    <Space direction="vertical" size={20} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Editor Dashboard</Typography.Title>
          <Typography.Text type="secondary">
            Your assigned production workload and due work.
          </Typography.Text>
        </div>
      </div>
      {dashboardQuery.isError ? (
        <Alert
          type="error"
          showIcon
          message="Unable to load editor dashboard"
          description="Refresh the page or try again after checking your connection."
        />
      ) : null}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Assigned Jobs"
              value={dashboard?.assigned_jobs ?? 0}
              loading={dashboardQuery.isLoading}
              prefix={<UserSwitchOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Due Today"
              value={dashboard?.due_today ?? 0}
              loading={dashboardQuery.isLoading}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Overdue"
              value={dashboard?.overdue ?? 0}
              loading={dashboardQuery.isLoading}
              prefix={<ExclamationCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Completed This Week"
              value={dashboard?.completed_this_week ?? 0}
              loading={dashboardQuery.isLoading}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Current Workload"
              value={dashboard?.current_workload ?? 0}
              loading={dashboardQuery.isLoading}
            />
          </Card>
        </Col>
      </Row>
    </Space>
  );
}
