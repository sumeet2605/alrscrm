import { EyeOutlined, PlusOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  App,
  Button,
  DatePicker,
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

import { createInvoice, listInvoices } from "../../api/finance";
import { useAuth } from "../../contexts/AuthContext";
import type { Invoice, InvoicePayload, InvoiceStatus } from "../../types/finance";
import {
  canManageFinance,
  invoiceStatusColor,
  invoiceStatuses,
  labelFromEnum,
  money
} from "./financeOptions";

type InvoiceFormValues = {
  organization_id: string;
  branch_id: string;
  family_id: string;
  booking_id: string;
  buyer_billing_name: string;
  buyer_billing_address?: string;
  buyer_state_code?: string;
  due_date?: dayjs.Dayjs;
  description: string;
  unit_price: string;
  cgst_amount?: string;
  sgst_amount?: string;
  igst_amount?: string;
};

export function InvoiceListPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { message } = App.useApp();
  const { user } = useAuth();
  const roleNames = user?.roles.map((role) => role.name) ?? [];
  const canManage = canManageFinance(roleNames);
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState<InvoiceStatus | undefined>();
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm<InvoiceFormValues>();
  const invoicesQuery = useQuery({
    queryKey: ["invoices", page, status],
    queryFn: () => listInvoices({ page, page_size: 10, invoice_status: status })
  });

  const createMutation = useMutation({
    mutationFn: createInvoice,
    onSuccess: async (invoice) => {
      message.success("Invoice created");
      setModalOpen(false);
      form.resetFields();
      await queryClient.invalidateQueries({ queryKey: ["invoices"] });
      await queryClient.invalidateQueries({ queryKey: ["finance-metrics"] });
      navigate(`/finance/invoices/${invoice.id}`);
    }
  });

  const columns: ColumnsType<Invoice> = [
    {
      title: "Invoice",
      dataIndex: "invoice_number",
      render: (value: string, invoice) => (
        <Button type="link" onClick={() => navigate(`/finance/invoices/${invoice.id}`)}>
          {value}
        </Button>
      )
    },
    {
      title: "Buyer",
      dataIndex: "buyer_billing_name"
    },
    {
      title: "Status",
      dataIndex: "invoice_status",
      render: (value: InvoiceStatus) => (
        <Tag color={invoiceStatusColor(value)}>{labelFromEnum(value)}</Tag>
      )
    },
    {
      title: "Total",
      dataIndex: "total_amount",
      render: (value: string) => money(value)
    },
    {
      title: "Balance",
      dataIndex: "balance_due",
      render: (value: string) => money(value)
    },
    {
      title: "Due Date",
      dataIndex: "due_date",
      render: (value?: string | null) => (value ? dayjs(value).format("DD MMM YYYY") : "-")
    },
    {
      title: "Actions",
      width: 96,
      render: (_, invoice) => (
        <Button
          icon={<EyeOutlined />}
          onClick={() => navigate(`/finance/invoices/${invoice.id}`)}
        />
      )
    }
  ];

  const submitInvoice = (values: InvoiceFormValues) => {
    const cgstAmount = values.cgst_amount ?? "0.00";
    const sgstAmount = values.sgst_amount ?? "0.00";
    const igstAmount = values.igst_amount ?? "0.00";
    const payload: InvoicePayload = {
      organization_id: values.organization_id,
      branch_id: values.branch_id,
      family_id: values.family_id,
      booking_id: values.booking_id,
      due_date: values.due_date?.format("YYYY-MM-DD"),
      buyer_billing_name: values.buyer_billing_name,
      buyer_billing_address: values.buyer_billing_address,
      buyer_state_code: values.buyer_state_code,
      supply_type: "INTRA_STATE",
      gst_registration_type: "UNREGISTERED",
      reverse_charge_applicable: false,
      line_items: [
        {
          description: values.description,
          quantity: "1",
          unit_price: values.unit_price,
          discount_amount: "0.00",
          tax_rate: "0.00",
          cgst_rate: "0.00",
          cgst_amount: cgstAmount,
          sgst_rate: "0.00",
          sgst_amount: sgstAmount,
          igst_rate: "0.00",
          igst_amount: igstAmount
        }
      ]
    };
    createMutation.mutate(payload);
  };

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Invoices</Typography.Title>
          <Typography.Text type="secondary">
            Manage tenant-scoped invoice records, GST snapshots, and receivables.
          </Typography.Text>
        </div>
        {canManage ? (
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
            New Invoice
          </Button>
        ) : null}
      </div>

      <Space wrap>
        <Select
          allowClear
          placeholder="Status"
          value={status}
          className="filter-control"
          options={invoiceStatuses.map((item) => ({ value: item, label: labelFromEnum(item) }))}
          onChange={(value) => {
            setPage(1);
            setStatus(value);
          }}
        />
      </Space>

      <Table<Invoice>
        rowKey="id"
        loading={invoicesQuery.isLoading}
        dataSource={invoicesQuery.data?.items ?? []}
        columns={columns}
        pagination={{
          current: page,
          pageSize: invoicesQuery.data?.meta.page_size ?? 10,
          total: invoicesQuery.data?.meta.total ?? 0,
          onChange: setPage
        }}
      />

      <Modal
        title="Create Invoice"
        open={modalOpen}
        okText="Create"
        confirmLoading={createMutation.isPending}
        onOk={() => form.submit()}
        onCancel={() => setModalOpen(false)}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={submitInvoice}
          initialValues={{
            organization_id: user?.organization_id,
            branch_id: user?.branch_id ?? undefined,
            description: "Photography service",
            unit_price: "0.00"
          }}
        >
          <Form.Item name="organization_id" label="Organization ID" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="branch_id" label="Branch ID" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="family_id" label="Family ID" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="booking_id" label="Booking ID" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="buyer_billing_name" label="Buyer Billing Name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="buyer_billing_address" label="Buyer Billing Address">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="buyer_state_code" label="Buyer State Code">
            <Input maxLength={2} />
          </Form.Item>
          <Form.Item name="due_date" label="Due Date">
            <DatePicker className="full-width" />
          </Form.Item>
          <Form.Item name="description" label="Line Description" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="unit_price" label="Line Price" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Space>
            <Form.Item name="cgst_amount" label="CGST">
              <Input />
            </Form.Item>
            <Form.Item name="sgst_amount" label="SGST">
              <Input />
            </Form.Item>
            <Form.Item name="igst_amount" label="IGST">
              <Input />
            </Form.Item>
          </Space>
        </Form>
      </Modal>
    </Space>
  );
}
