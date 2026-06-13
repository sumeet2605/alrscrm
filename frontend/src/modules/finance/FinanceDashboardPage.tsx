import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  FileTextOutlined,
  WalletOutlined
} from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { Alert, Card, Col, Row, Space, Statistic, Typography } from "antd";

import { getFinanceMetrics } from "../../api/finance";
import { invoiceStatuses, labelFromEnum, money, paymentMethods } from "./financeOptions";

export function FinanceDashboardPage() {
  const metricsQuery = useQuery({
    queryKey: ["finance-metrics"],
    queryFn: getFinanceMetrics
  });
  const metrics = metricsQuery.data;

  return (
    <Space direction="vertical" size={20} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Finance Dashboard</Typography.Title>
          <Typography.Text type="secondary">
            Track invoiced receivables, collections, overdue exposure, and GST-backed billing.
          </Typography.Text>
        </div>
      </div>

      {metricsQuery.isError ? (
        <Alert
          type="error"
          showIcon
          message="Unable to load finance metrics"
          description="Refresh the page or try again after checking your connection."
        />
      ) : null}

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Revenue This Month"
              value={Number(metrics?.revenue_this_month ?? 0)}
              formatter={() => money(metrics?.revenue_this_month)}
              loading={metricsQuery.isLoading}
              prefix={<WalletOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Revenue This Year"
              value={Number(metrics?.revenue_this_year ?? 0)}
              formatter={() => money(metrics?.revenue_this_year)}
              loading={metricsQuery.isLoading}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Outstanding"
              value={Number(metrics?.outstanding_amount ?? 0)}
              formatter={() => money(metrics?.outstanding_amount)}
              loading={metricsQuery.isLoading}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} xl={6}>
          <Card>
            <Statistic
              title="Overdue"
              value={Number(metrics?.overdue_amount ?? 0)}
              formatter={() => money(metrics?.overdue_amount)}
              loading={metricsQuery.isLoading}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="Invoices By Status" loading={metricsQuery.isLoading}>
            <Space direction="vertical" className="page-stack">
              {invoiceStatuses.map((status) => (
                <Row key={status} justify="space-between">
                  <Typography.Text>{labelFromEnum(status)}</Typography.Text>
                  <Typography.Text strong>{metrics?.invoices_by_status[status] ?? 0}</Typography.Text>
                </Row>
              ))}
            </Space>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Payments By Method" loading={metricsQuery.isLoading}>
            <Space direction="vertical" className="page-stack">
              {paymentMethods.map((method) => (
                <Row key={method} justify="space-between">
                  <Typography.Text>{labelFromEnum(method)}</Typography.Text>
                  <Typography.Text strong>{metrics?.payments_by_method[method] ?? 0}</Typography.Text>
                </Row>
              ))}
            </Space>
          </Card>
        </Col>
      </Row>
    </Space>
  );
}
