import {
  CloseCircleOutlined,
  DownloadOutlined,
  SendOutlined,
  WalletOutlined
} from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  App,
  Button,
  Card,
  Descriptions,
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
import { useNavigate, useParams } from "react-router-dom";

import {
  createPayment,
  downloadInvoicePdf,
  getInvoice,
  issueInvoice,
  voidInvoice
} from "../../api/finance";
import { useAuth } from "../../contexts/AuthContext";
import type {
  InvoiceLineItem,
  InvoiceStatus,
  Payment,
  PaymentMethod,
  PaymentPayload
} from "../../types/finance";
import {
  canManageFinance,
  invoiceStatusColor,
  labelFromEnum,
  money,
  paymentMethods,
  paymentStatusColor
} from "./financeOptions";

type PaymentFormValues = {
  amount: string;
  payment_method: PaymentMethod;
  transaction_reference?: string;
  notes?: string;
};

function saveBlob(blob: Blob, fileName: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  link.click();
  URL.revokeObjectURL(url);
}

export function InvoiceDetailPage() {
  const { invoiceId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { message } = App.useApp();
  const { user } = useAuth();
  const roleNames = user?.roles.map((role) => role.name) ?? [];
  const canManage = canManageFinance(roleNames);
  const [paymentModalOpen, setPaymentModalOpen] = useState(false);
  const [form] = Form.useForm<PaymentFormValues>();
  const invoiceQuery = useQuery({
    queryKey: ["invoice", invoiceId],
    queryFn: () => getInvoice(invoiceId!),
    enabled: Boolean(invoiceId)
  });
  const invoice = invoiceQuery.data;

  const refresh = async () => {
    await queryClient.invalidateQueries({ queryKey: ["invoice", invoiceId] });
    await queryClient.invalidateQueries({ queryKey: ["invoices"] });
    await queryClient.invalidateQueries({ queryKey: ["payments"] });
    await queryClient.invalidateQueries({ queryKey: ["finance-metrics"] });
  };

  const issueMutation = useMutation({
    mutationFn: issueInvoice,
    onSuccess: async () => {
      message.success("Invoice issued");
      await refresh();
    }
  });
  const voidMutation = useMutation({
    mutationFn: voidInvoice,
    onSuccess: async () => {
      message.success("Invoice voided");
      await refresh();
    }
  });
  const paymentMutation = useMutation({
    mutationFn: createPayment,
    onSuccess: async () => {
      message.success("Payment recorded");
      setPaymentModalOpen(false);
      form.resetFields();
      await refresh();
    }
  });
  const pdfMutation = useMutation({
    mutationFn: downloadInvoicePdf,
    onSuccess: (blob) => {
      if (invoice) {
        saveBlob(blob, `${invoice.invoice_number}.pdf`);
      }
    }
  });

  const lineColumns: ColumnsType<InvoiceLineItem> = [
    { title: "Description", dataIndex: "description" },
    { title: "Qty", dataIndex: "quantity" },
    { title: "Unit Price", dataIndex: "unit_price", render: (value: string) => money(value) },
    { title: "Taxable", dataIndex: "taxable_amount", render: (value: string) => money(value) },
    { title: "CGST", dataIndex: "cgst_amount", render: (value: string) => money(value) },
    { title: "SGST", dataIndex: "sgst_amount", render: (value: string) => money(value) },
    { title: "IGST", dataIndex: "igst_amount", render: (value: string) => money(value) },
    { title: "Total", dataIndex: "line_total", render: (value: string) => money(value) }
  ];

  const paymentColumns: ColumnsType<Payment> = [
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
      render: (value: Payment["payment_status"]) => (
        <Tag color={paymentStatusColor(value)}>{labelFromEnum(value)}</Tag>
      )
    },
    {
      title: "Received",
      dataIndex: "received_date",
      render: (value: string) => dayjs(value).format("DD MMM YYYY")
    }
  ];

  const submitPayment = (values: PaymentFormValues) => {
    if (!invoice) return;
    const payload: PaymentPayload = {
      invoice_id: invoice.id,
      amount: values.amount,
      payment_method: values.payment_method,
      payment_status: "COMPLETED",
      transaction_reference: values.transaction_reference,
      notes: values.notes
    };
    paymentMutation.mutate(payload);
  };

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>{invoice?.invoice_number ?? "Invoice"}</Typography.Title>
          <Typography.Text type="secondary">
            Invoice is the financial source of truth for this booking.
          </Typography.Text>
        </div>
        {canManage && invoice ? (
          <Space wrap>
            <Button
              icon={<DownloadOutlined />}
              onClick={() => pdfMutation.mutate(invoice.id)}
              loading={pdfMutation.isPending}
            >
              GST PDF
            </Button>
            <Button
              icon={<SendOutlined />}
              onClick={() => issueMutation.mutate(invoice.id)}
              disabled={invoice.invoice_status !== "DRAFT"}
            >
              Issue
            </Button>
            <Button
              icon={<WalletOutlined />}
              type="primary"
              onClick={() => setPaymentModalOpen(true)}
              disabled={["DRAFT", "VOID", "PAID"].includes(invoice.invoice_status)}
            >
              Record Payment
            </Button>
            <Button
              danger
              icon={<CloseCircleOutlined />}
              onClick={() => voidMutation.mutate(invoice.id)}
              disabled={!["DRAFT", "ISSUED"].includes(invoice.invoice_status)}
            >
              Void
            </Button>
          </Space>
        ) : null}
      </div>

      <Card loading={invoiceQuery.isLoading}>
        {invoice ? (
          <Descriptions column={{ xs: 1, md: 2 }} bordered size="small">
            <Descriptions.Item label="Status">
              <Tag color={invoiceStatusColor(invoice.invoice_status as InvoiceStatus)}>
                {labelFromEnum(invoice.invoice_status)}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Buyer">{invoice.buyer_billing_name}</Descriptions.Item>
            <Descriptions.Item label="Total">{money(invoice.total_amount)}</Descriptions.Item>
            <Descriptions.Item label="Paid">{money(invoice.amount_paid)}</Descriptions.Item>
            <Descriptions.Item label="Balance">{money(invoice.balance_due)}</Descriptions.Item>
            <Descriptions.Item label="Due Date">
              {invoice.due_date ? dayjs(invoice.due_date).format("DD MMM YYYY") : "-"}
            </Descriptions.Item>
            <Descriptions.Item label="GST Registration">
              {labelFromEnum(invoice.gst_registration_type)}
            </Descriptions.Item>
            <Descriptions.Item label="Supply Type">
              {labelFromEnum(invoice.supply_type)}
            </Descriptions.Item>
            <Descriptions.Item label="Seller GSTIN">{invoice.seller_gstin ?? "-"}</Descriptions.Item>
            <Descriptions.Item label="Buyer GSTIN">{invoice.buyer_gstin ?? "-"}</Descriptions.Item>
            <Descriptions.Item label="Place Of Supply">
              {invoice.place_of_supply_state_code ?? "-"}
            </Descriptions.Item>
            <Descriptions.Item label="Reverse Charge">
              {invoice.reverse_charge_applicable ? "Yes" : "No"}
            </Descriptions.Item>
          </Descriptions>
        ) : null}
      </Card>

      <Card title="Line Items">
        <Table<InvoiceLineItem>
          rowKey="id"
          dataSource={invoice?.line_items ?? []}
          columns={lineColumns}
          pagination={false}
        />
      </Card>

      <Card title="Payments">
        <Table<Payment>
          rowKey="id"
          dataSource={invoice?.payments ?? []}
          columns={paymentColumns}
          pagination={false}
        />
      </Card>

      <Modal
        title="Record Payment"
        open={paymentModalOpen}
        okText="Record"
        confirmLoading={paymentMutation.isPending}
        onOk={() => form.submit()}
        onCancel={() => setPaymentModalOpen(false)}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={submitPayment}
          initialValues={{
            amount: invoice?.balance_due ?? "0.00",
            payment_method: "UPI"
          }}
        >
          <Form.Item name="amount" label="Amount" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="payment_method" label="Method" rules={[{ required: true }]}>
            <Select
              options={paymentMethods.map((method) => ({
                value: method,
                label: labelFromEnum(method)
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
