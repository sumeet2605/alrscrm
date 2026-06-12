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

import { listBookings } from "../../api/bookings";
import { listFamilies } from "../../api/families";
import { createInvoice, listInvoices } from "../../api/finance";
import { getOrganization, listBranches } from "../../api/identity";
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
  service_type: string;
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
  const organizationQuery = useQuery({
    queryKey: ["organization", user?.organization_id],
    queryFn: () => getOrganization(user!.organization_id),
    enabled: Boolean(user?.organization_id)
  });
  const branchesQuery = useQuery({
    queryKey: ["branches", "invoice-form"],
    queryFn: () => listBranches({ page: 1, page_size: 100 })
  });
  const familiesQuery = useQuery({
    queryKey: ["families", "invoice-form"],
    queryFn: () => listFamilies({ page: 1, page_size: 100 })
  });
  const bookingsQuery = useQuery({
    queryKey: ["bookings", "invoice-form"],
    queryFn: () => listBookings({ page: 1, page_size: 100 })
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
    const selectedBranch = branchesQuery.data?.items.find((branch) => branch.id === values.branch_id);
    const cgstAmount = values.cgst_amount ?? "0.00";
    const sgstAmount = values.sgst_amount ?? "0.00";
    const igstAmount = values.igst_amount ?? "0.00";
    const payload: InvoicePayload = {
      organization_id: selectedBranch?.organization_id ?? values.organization_id,
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
          service_type: values.service_type,
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

  const openCreateModal = () => {
    form.setFieldsValue({
      organization_id: user?.organization_id,
      branch_id: user?.branch_id ?? branchesQuery.data?.items[0]?.id,
      description: "Photography service",
      unit_price: "0.00",
      service_type: "NEWBORN"
    });
    setModalOpen(true);
  };

  const formatAddress = (familyId?: string) => {
    const family = familiesQuery.data?.items.find((item) => item.id === familyId);
    if (!family?.address) {
      return family?.city ?? undefined;
    }
    return [
      family.address.address_line_1,
      family.address.address_line_2,
      family.address.city,
      family.address.state,
      family.address.country,
      family.address.postal_code
    ]
      .filter(Boolean)
      .join(", ");
  };

  const applyFamilyDefaults = (familyId: string) => {
    const family = familiesQuery.data?.items.find((item) => item.id === familyId);
    if (!family) return;
    form.setFieldsValue({
      organization_id: family.organization_id,
      branch_id: family.branch_id,
      family_id: family.id,
      buyer_billing_name: family.primary_contact_name,
      buyer_billing_address: formatAddress(family.id)
    });
  };

  const applyBookingDefaults = (bookingId: string) => {
    const booking = bookingsQuery.data?.items.find((item) => item.id === bookingId);
    if (!booking) return;
    const firstItem = booking.items[0];
    form.setFieldsValue({
      organization_id: booking.organization_id,
      branch_id: booking.branch_id,
      family_id: booking.family_id,
      booking_id: booking.id,
      buyer_billing_name: booking.family?.primary_contact_name,
      buyer_billing_address: formatAddress(booking.family_id),
      description: firstItem?.package?.name ?? "Photography service",
      unit_price: firstItem?.final_amount ?? booking.total_amount ?? "0.00",
      service_type: firstItem?.service_type ?? booking.opportunity?.opportunity_type ?? "NEWBORN"
    });
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
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreateModal}>
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
            description: "Photography service",
            unit_price: "0.00",
            service_type: "NEWBORN"
          }}
        >
          <Form.Item name="organization_id" hidden rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Organization">
            <Input
              disabled
              value={organizationQuery.data?.name ?? "Current organization"}
            />
          </Form.Item>
          <Form.Item name="branch_id" label="Branch" rules={[{ required: true }]}>
            <Select
              loading={branchesQuery.isLoading}
              options={(branchesQuery.data?.items ?? []).map((branch) => ({
                value: branch.id,
                label: branch.city ? `${branch.name} · ${branch.city}` : branch.name
              }))}
            />
          </Form.Item>
          <Form.Item name="family_id" label="Family" rules={[{ required: true }]}>
            <Select
              showSearch
              optionFilterProp="label"
              loading={familiesQuery.isLoading}
              onChange={applyFamilyDefaults}
              options={(familiesQuery.data?.items ?? []).map((family) => ({
                value: family.id,
                label: `${family.family_code} · ${family.primary_contact_name} · ${family.primary_contact_phone}`
              }))}
            />
          </Form.Item>
          <Form.Item
            noStyle
            shouldUpdate={(previous, current) => previous.family_id !== current.family_id}
          >
            {({ getFieldValue }) => {
              const familyId = getFieldValue("family_id");
              return (
                <Form.Item name="booking_id" label="Booking" rules={[{ required: true }]}>
                  <Select
                    showSearch
                    optionFilterProp="label"
                    loading={bookingsQuery.isLoading}
                    onChange={applyBookingDefaults}
                    options={(bookingsQuery.data?.items ?? [])
                      .filter((booking) => !familyId || booking.family_id === familyId)
                      .map((booking) => ({
                        value: booking.id,
                        label: `${booking.booking_number} · ${
                          booking.family?.primary_contact_name ?? "Family"
                        } · ${money(booking.total_amount)}`
                      }))}
                  />
                </Form.Item>
              );
            }}
          </Form.Item>
          <Form.Item name="service_type" hidden>
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
