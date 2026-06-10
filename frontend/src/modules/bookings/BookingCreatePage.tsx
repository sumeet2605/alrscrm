import { ArrowLeftOutlined, SaveOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { App, Button, Card, DatePicker, Form, Input, InputNumber, Select, Space, Statistic, Typography } from "antd";
import dayjs from "dayjs";
import { useMemo } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { createBooking, listAddons, listPackages } from "../../api/bookings";
import { listFamilies } from "../../api/families";
import { listOpportunities } from "../../api/sales";
import { useAuth } from "../../contexts/AuthContext";
import type { BookingPayload } from "../../types/bookings";
import { canManageBookings, labelFromEnum, serviceTypes } from "./bookingOptions";

interface BookingFormValues extends Omit<BookingPayload, "booking_date"> {
  booking_date?: dayjs.Dayjs;
}

export function BookingCreatePage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { message } = App.useApp();
  const { user } = useAuth();
  const roleNames = user?.roles.map((role) => role.name) ?? [];
  const [form] = Form.useForm<BookingFormValues>();
  const watchedItems = Form.useWatch("items", form) ?? [];
  const watchedAdvance = Form.useWatch("advance_received", form) ?? 0;
  const familiesQuery = useQuery({ queryKey: ["families", "booking-form"], queryFn: () => listFamilies({ page: 1, page_size: 100 }) });
  const opportunitiesQuery = useQuery({ queryKey: ["opportunities", "booked"], queryFn: () => listOpportunities({ page: 1, page_size: 100, stage: "BOOKED" }) });
  const packagesQuery = useQuery({ queryKey: ["packages"], queryFn: listPackages });
  const addonsQuery = useQuery({ queryKey: ["addons"], queryFn: listAddons });
  const totals = useMemo(() => {
    const total = watchedItems.reduce((sum, item) => {
      const selectedPackage = packagesQuery.data?.find((pkg) => pkg.id === item?.package_id);
      const packagePrice = Number(selectedPackage?.price ?? 0);
      const discount = Number(item?.discount ?? 0);
      const addonTotal = (item?.addons ?? []).reduce((addonSum, addon) => {
        const selectedAddon = addonsQuery.data?.find((entry) => entry.id === addon?.addon_id);
        return addonSum + Number(selectedAddon?.price ?? 0);
      }, 0);
      return sum + Math.max(packagePrice - discount, 0) + addonTotal;
    }, 0);
    return { total, balance: Math.max(total - Number(watchedAdvance ?? 0), 0) };
  }, [addonsQuery.data, packagesQuery.data, watchedAdvance, watchedItems]);
  const createMutation = useMutation({
    mutationFn: (values: BookingFormValues) => {
      const family = familiesQuery.data?.items.find((item) => item.id === values.family_id);
      const items = values.items.map((item) => ({
        ...item,
        addons: (item.addons ?? []).map((addon) =>
          typeof addon === "string" ? { addon_id: addon } : addon
        )
      }));
      return createBooking({
        ...values,
        items,
        organization_id: family?.organization_id ?? values.organization_id,
        branch_id: family?.branch_id ?? values.branch_id,
        booking_date: values.booking_date?.format("YYYY-MM-DD") ?? dayjs().format("YYYY-MM-DD")
      });
    },
    onSuccess: async (booking) => {
      message.success("Booking created");
      await queryClient.invalidateQueries({ queryKey: ["bookings"] });
      navigate(`/bookings/${booking.id}`);
    }
  });

  if (!canManageBookings(roleNames)) {
    return <Navigate to="/bookings" replace />;
  }

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>New Booking</Typography.Title>
          <Typography.Text type="secondary">Create fulfillment from a booked opportunity.</Typography.Text>
        </div>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/bookings")}>Back</Button>
      </div>
      <Card>
        <Form form={form} layout="vertical" requiredMark={false} initialValues={{ organization_id: user?.organization_id, branch_id: user?.branch_id, booking_status: "CONFIRMED", advance_received: 0, booking_date: dayjs(), items: [{}] }} onFinish={(values) => createMutation.mutate(values)}>
          <Form.Item name="organization_id" hidden><Input /></Form.Item>
          <Form.Item name="branch_id" hidden><Input /></Form.Item>
          <div className="form-grid">
            <Form.Item label="Family" name="family_id" rules={[{ required: true, message: "Family is required" }]}>
              <Select showSearch optionFilterProp="label" onChange={(familyId) => {
                const family = familiesQuery.data?.items.find((item) => item.id === familyId);
                form.setFieldsValue({ organization_id: family?.organization_id, branch_id: family?.branch_id });
              }} options={(familiesQuery.data?.items ?? []).map((family) => ({ value: family.id, label: `${family.family_code} · ${family.primary_contact_name} · ${family.primary_contact_phone}` }))} />
            </Form.Item>
            <Form.Item label="Booked Opportunity" name="opportunity_id" rules={[{ required: true, message: "Booked opportunity is required" }]}>
              <Select showSearch optionFilterProp="label" options={(opportunitiesQuery.data?.items ?? []).map((opportunity) => ({ value: opportunity.id, label: `${opportunity.family?.family_code ?? ""} · ${labelFromEnum(opportunity.opportunity_type)} · ₹${Number(opportunity.estimated_value).toLocaleString("en-IN")}` }))} />
            </Form.Item>
            <Form.Item label="Booking Date" name="booking_date" rules={[{ required: true }]}><DatePicker className="full-width-control" /></Form.Item>
            <Form.Item label="Advance Received" name="advance_received"><InputNumber min={0} className="full-width-control" /></Form.Item>
          </div>
          <Form.List name="items">
            {(fields, { add, remove }) => (
              <Space direction="vertical" size={12} className="page-stack">
                {fields.map((field) => (
                  <Card key={field.key} size="small" title={`Booking Item ${field.name + 1}`} extra={fields.length > 1 ? <Button onClick={() => remove(field.name)}>Remove</Button> : null}>
                    <div className="form-grid">
                      <Form.Item label="Package" name={[field.name, "package_id"]} rules={[{ required: true }]}><Select options={(packagesQuery.data ?? []).filter((pkg) => pkg.is_active).map((pkg) => ({ value: pkg.id, label: `${pkg.name} · ₹${Number(pkg.price).toLocaleString("en-IN")}` }))} /></Form.Item>
                      <Form.Item label="Service" name={[field.name, "service_type"]} rules={[{ required: true }]}><Select options={serviceTypes.map((value) => ({ value, label: labelFromEnum(value) }))} /></Form.Item>
                      <Form.Item label="Discount" name={[field.name, "discount"]}><InputNumber min={0} className="full-width-control" /></Form.Item>
                      <Form.Item label="Addons" name={[field.name, "addons"]}><Select mode="multiple" labelInValue={false} options={(addonsQuery.data ?? []).filter((addon) => addon.is_active).map((addon) => ({ value: addon.id, label: `${addon.name} · ₹${Number(addon.price).toLocaleString("en-IN")}` }))} onChange={(ids) => {
                        const current = form.getFieldValue("items") ?? [];
                        current[field.name] = { ...current[field.name], addons: ids.map((addon_id: string) => ({ addon_id })) };
                        form.setFieldsValue({ items: current });
                      }} /></Form.Item>
                    </div>
                  </Card>
                ))}
                <Button onClick={() => add({ discount: 0, addons: [] })}>Add Package</Button>
              </Space>
            )}
          </Form.List>
          <Form.Item label="Notes" name="notes"><Input.TextArea rows={4} /></Form.Item>
          <div className="form-actions">
            <Statistic title="Total" value={totals.total} prefix="₹" precision={0} />
            <Statistic title="Balance" value={totals.balance} prefix="₹" precision={0} />
            <Button type="primary" icon={<SaveOutlined />} htmlType="submit" loading={createMutation.isPending}>Save Booking</Button>
          </div>
        </Form>
      </Card>
    </Space>
  );
}
