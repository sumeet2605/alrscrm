import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  DownloadOutlined,
  ReloadOutlined
} from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { Alert, Card, Col, Row, Space, Statistic, Typography } from "antd";

import { getDeliveryMetrics } from "../../api/delivery";

export function DeliveryDashboardPage() {
  const metricsQuery = useQuery({
    queryKey: ["delivery-metrics"],
    queryFn: getDeliveryMetrics
  });
  const metrics = metricsQuery.data;

  return (
    <Space direction="vertical" size={20} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Delivery Dashboard</Typography.Title>
          <Typography.Text type="secondary">
            Track client delivery readiness, downloads, expiry, and reopen demand.
          </Typography.Text>
        </div>
      </div>

      {metricsQuery.isError ? (
        <Alert
          type="error"
          showIcon
          message="Unable to load delivery metrics"
          description="Refresh the page or try again after checking your connection."
        />
      ) : null}

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Pending Delivery"
              value={metrics?.pending_delivery ?? 0}
              loading={metricsQuery.isLoading}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Ready Delivery"
              value={metrics?.ready_delivery ?? 0}
              loading={metricsQuery.isLoading}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Delivered"
              value={metrics?.delivered ?? 0}
              loading={metricsQuery.isLoading}
              prefix={<DownloadOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Reopened"
              value={metrics?.reopened ?? 0}
              loading={metricsQuery.isLoading}
              prefix={<ReloadOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Expired"
              value={metrics?.expired ?? 0}
              loading={metricsQuery.isLoading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Average Delivery TAT"
              value={metrics?.average_delivery_tat ?? 0}
              suffix="days"
              precision={1}
              loading={metricsQuery.isLoading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Downloads This Month"
              value={metrics?.downloads_this_month ?? 0}
              loading={metricsQuery.isLoading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Re-download Potential"
              value={Number(metrics?.re_download_revenue_potential ?? 0)}
              prefix="₹"
              loading={metricsQuery.isLoading}
            />
          </Card>
        </Col>
      </Row>
    </Space>
  );
}

