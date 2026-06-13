import { EyeOutlined, PlusOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  App,
  Button,
  Form,
  Input,
  Modal,
  Select,
  Space,
  Table,
  Tag,
  Typography
} from "antd";
import type { ColumnsType } from "antd/es/table";
import dayjs from "dayjs";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { createPayment, listPayments } from "../../api/finance";
import { useAuth } from "../../contexts/AuthContext";
import type { Payment, PaymentMethod, PaymentPayload, PaymentStatus } from "../../types/finance";
import {
  canManageFinance,
  labelFromEnum,
  money,
  paymentMethods,
  paymentStatusColor,
  paymentStatuses
} from "./financeOptions";

type PaymentFormValues = {
  invoice_id: string;
  amount: string;
  payment_method: PaymentMethod;
  payment_status: PaymentStatus;
  transaction_reference?: string;
  notes?: string;
};

export function PaymentListPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { message } = App.useApp();
  const { user } = useAuth();
  const roleNames = user?.roles.map((role) => role.name) ?? [];
  const canManage = canManageFinance(roleNames);
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState<PaymentStatus | undefined>();
  const [method, setMethod] = useState<PaymentMethod | undefined>();
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm<PaymentFormValues>();
  const paymentsQuery = useQuery({
    queryKey: ["payments", page, status, method],
    queryFn: () =>
      listPayments({
        page,
        page_size: 10,
        payment_status: status,
        payment_method: method
      })
  });

  const createMutation = useMutation({
    mutationFn: createPayment,
    onSuccess: async (payment) => {
      message.success("Payment recorded");
      setModalOpen(false);
      form.resetFields();
      await queryClient.invalidateQueries({ queryKey: ["payments"] });
      await queryClient.invalidateQueries({ queryKey: ["invoices"] });
      await queryClient.invalidateQueries({ queryKey: ["finance-metrics"] });
      navigate(`/finance/payments/${payment.id}`);
    }
  });

  const columns: ColumnsType<Payment> = [
    {
      title: "Payment",
      dataIndex: "payment_number",
      render: (value: string, payment) => (
        <Button type="link" onClick={() => navigate(`/finance/payments/${payment.id}`)}>
          {value}
        </Button>
      )
    },
    { title: "Amount", dataIndex: "amount", render: (value: string) => money(value) },
    { title: "Method", dataIndex: "payment_method", render: (value: string) => labelFromEnum(value) },
    {
      title: "Status",
      dataIndex: "payment_status",
      render: (value: PaymentStatus) => (
        <Tag color={paymentStatusColor(value)}>{labelFromEnum(value)}</Tag>
      )
    },
    {
      title: "Received",
      dataIndex: "received_date",
      render: (value: string) => dayjs(value).format("DD MMM YYYY")
    },
    {
      title: "Actions",
      width: 96,
      render: (_, payment) => (
        <Button
          icon={<EyeOutlined />}
          onClick={() => navigate(`/finance/payments/${payment.id}`)}
        />
      )
    }
  ];

  const submitPayment = (values: PaymentFormValues) => {
    const payload: PaymentPayload = {
      invoice_id: values.invoice_id,
      amount: values.amount,
      payment_method: values.payment_method,
      payment_status: values.payment_status,
      transaction_reference: values.transaction_reference,
      notes: values.notes
    };
    createMutation.mutate(payload);
  };

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Payments</Typography.Title>
          <Typography.Text type="secondary">
            Track payments received against finance-owned invoices.
          </Typography.Text>
        </div>
        {canManage ? (
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
            New Payment
          </Button>
        ) : null}
      </div>

      <Space wrap>
        <Select
          allowClear
          placeholder="Status"
          value={status}
          className="filter-control"
          options={paymentStatuses.map((item) => ({ value: item, label: labelFromEnum(item) }))}
          onChange={(value) => {
            setPage(1);
            setStatus(value);
          }}
        />
        <Select
          allowClear
          placeholder="Method"
          value={method}
          className="filter-control"
          options={paymentMethods.map((item) => ({ value: item, label: labelFromEnum(item) }))}
          onChange={(value) => {
            setPage(1);
            setMethod(value);
          }}
        />
      </Space>

      <Table<Payment>
        rowKey="id"
        loading={paymentsQuery.isLoading}
        dataSource={paymentsQuery.data?.items ?? []}
        columns={columns}
        pagination={{
          current: page,
          pageSize: paymentsQuery.data?.meta.page_size ?? 10,
          total: paymentsQuery.data?.meta.total ?? 0,
          onChange: setPage
        }}
      />

      <Modal
        title="Record Payment"
        open={modalOpen}
        okText="Record"
        confirmLoading={createMutation.isPending}
        onOk={() => form.submit()}
        onCancel={() => setModalOpen(false)}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={submitPayment}
          initialValues={{ payment_method: "UPI", payment_status: "COMPLETED" }}
        >
          <Form.Item name="invoice_id" label="Invoice ID" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="amount" label="Amount" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="payment_method" label="Method" rules={[{ required: true }]}>
            <Select
              options={paymentMethods.map((item) => ({ value: item, label: labelFromEnum(item) }))}
            />
          </Form.Item>
          <Form.Item name="payment_status" label="Status" rules={[{ required: true }]}>
            <Select
              options={paymentStatuses.map((item) => ({
                value: item,
                label: labelFromEnum(item)
              }))}
            />
          </Form.Item>
          <Form.Item name="transaction_reference" label="Transaction Reference">
            <Input />
          </Form.Item>
          <Form.Item name="notes" label="Notes">
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </Space>
  );
}
