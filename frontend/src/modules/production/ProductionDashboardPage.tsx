import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  FieldTimeOutlined,
  InboxOutlined
} from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { Card, Col, Row, Space, Statistic, Table, Tag, Typography } from "antd";

import { getEditingMetrics } from "../../api/editing";
import type { EditingPriority } from "../../types/editing";
import { labelFromEnum, priorityColor } from "./editingOptions";

export function ProductionDashboardPage() {
  const metricsQuery = useQuery({
    queryKey: ["editing-metrics"],
    queryFn: getEditingMetrics
  });
  const metrics = metricsQuery.data;

  return (
    <Space direction="vertical" size={20} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Production Dashboard</Typography.Title>
          <Typography.Text type="secondary">
            Track editing throughput, review queues, and delivery readiness.
          </Typography.Text>
        </div>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Pending Jobs"
              value={metrics?.pending_jobs ?? 0}
              loading={metricsQuery.isLoading}
              prefix={<InboxOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="In Progress"
              value={metrics?.in_progress_jobs ?? 0}
              loading={metricsQuery.isLoading}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Ready For Review"
              value={metrics?.ready_for_review ?? 0}
              loading={metricsQuery.isLoading}
              prefix={<FieldTimeOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Ready For Delivery"
              value={metrics?.ready_for_delivery ?? 0}
              loading={metricsQuery.isLoading}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Overdue Jobs"
              value={metrics?.overdue_jobs ?? 0}
              loading={metricsQuery.isLoading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Average Editing TAT"
              value={metrics?.average_editing_tat ?? 0}
              suffix="days"
              precision={1}
              loading={metricsQuery.isLoading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Average Review TAT"
              value={metrics?.average_review_tat ?? 0}
              suffix="days"
              precision={1}
              loading={metricsQuery.isLoading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Photos Edited This Month"
              value={metrics?.photos_edited_this_month ?? 0}
              loading={metricsQuery.isLoading}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={8}>
          <Card title="Jobs By Priority">
            <Table
              rowKey="priority"
              pagination={false}
              dataSource={Object.entries(metrics?.jobs_by_priority ?? {}).map(([priority, count]) => ({
                priority,
                count
              }))}
              columns={[
                {
                  title: "Priority",
                  dataIndex: "priority",
                  render: (priority: string) => (
                    <Tag color={priorityColor(priority as EditingPriority)}>
                      {labelFromEnum(priority)}
                    </Tag>
                  )
                },
                { title: "Jobs", dataIndex: "count" }
              ]}
            />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Jobs By Service">
            <Table
              rowKey="service"
              pagination={false}
              dataSource={Object.entries(metrics?.jobs_by_service_type ?? {}).map(([service, count]) => ({
                service,
                count
              }))}
              columns={[
                { title: "Service", dataIndex: "service", render: (value: string) => labelFromEnum(value) },
                { title: "Jobs", dataIndex: "count" }
              ]}
            />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Jobs By Editor">
            <Table
              rowKey="editor"
              pagination={false}
              dataSource={Object.entries(metrics?.jobs_by_editor ?? {}).map(([editor, count]) => ({
                editor,
                count
              }))}
              columns={[
                { title: "Editor", dataIndex: "editor" },
                { title: "Jobs", dataIndex: "count" }
              ]}
            />
          </Card>
        </Col>
      </Row>
    </Space>
  );
}
