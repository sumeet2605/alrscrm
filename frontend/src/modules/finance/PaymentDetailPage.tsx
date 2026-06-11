import { useQuery } from "@tanstack/react-query";
import { Alert, Card, Descriptions, Space, Tag, Typography } from "antd";
import dayjs from "dayjs";
import { useParams } from "react-router-dom";

import { getPayment } from "../../api/finance";
import { labelFromEnum, money, paymentStatusColor } from "./financeOptions";

export function PaymentDetailPage() {
  const { paymentId } = useParams();
  const paymentQuery = useQuery({
    queryKey: ["payment", paymentId],
    queryFn: () => getPayment(paymentId!),
    enabled: Boolean(paymentId)
  });
  const payment = paymentQuery.data;

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>{payment?.payment_number ?? "Payment"}</Typography.Title>
          <Typography.Text type="secondary">
            Payment receipt details linked to the source invoice.
          </Typography.Text>
        </div>
      </div>

      {paymentQuery.isError ? (
        <Alert
          type="error"
          showIcon
          message="Unable to load payment"
          description="Refresh the page or try again after checking your connection."
        />
      ) : null}

      <Card loading={paymentQuery.isLoading}>
        {payment ? (
          <Descriptions column={{ xs: 1, md: 2 }} bordered size="small">
            <Descriptions.Item label="Status">
              <Tag color={paymentStatusColor(payment.payment_status)}>
                {labelFromEnum(payment.payment_status)}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Amount">{money(payment.amount)}</Descriptions.Item>
            <Descriptions.Item label="Method">
              {labelFromEnum(payment.payment_method)}
            </Descriptions.Item>
            <Descriptions.Item label="Received Date">
              {dayjs(payment.received_date).format("DD MMM YYYY")}
            </Descriptions.Item>
            <Descriptions.Item label="Invoice ID">{payment.invoice_id}</Descriptions.Item>
            <Descriptions.Item label="Reference">
              {payment.transaction_reference ?? "-"}
            </Descriptions.Item>
            <Descriptions.Item label="Notes" span={2}>
              {payment.notes ?? "-"}
            </Descriptions.Item>
          </Descriptions>
        ) : null}
      </Card>
    </Space>
  );
}
