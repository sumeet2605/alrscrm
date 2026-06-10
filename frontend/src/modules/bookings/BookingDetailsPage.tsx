import { ArrowLeftOutlined, PlusOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button, Card, DatePicker, Descriptions, Form, Input, List, Modal, Select, Space, Tag, Typography, message } from "antd";
import dayjs from "dayjs";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { createAssignment, createSchedule, getBooking } from "../../api/bookings";
import { listUsers } from "../../api/identity";
import { useAuth } from "../../contexts/AuthContext";
import type { AssignmentPayload, SchedulePayload } from "../../types/bookings";
import { assignmentRoles, canAssignPhotographers, canManageBookings, labelFromEnum, shootStatuses } from "./bookingOptions";

interface ScheduleFormValues extends Omit<SchedulePayload, "scheduled_start" | "scheduled_end"> {
  scheduled_start?: dayjs.Dayjs;
  scheduled_end?: dayjs.Dayjs;
}

export function BookingDetailsPage() {
  const { bookingId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const roleNames = user?.roles.map((role) => role.name) ?? [];
  const [isScheduleOpen, setIsScheduleOpen] = useState(false);
  const [assignmentScheduleId, setAssignmentScheduleId] = useState<string | null>(null);
  const [scheduleForm] = Form.useForm<ScheduleFormValues>();
  const [assignmentForm] = Form.useForm<AssignmentPayload>();
  const bookingQuery = useQuery({ queryKey: ["bookings", bookingId], queryFn: () => getBooking(bookingId!), enabled: Boolean(bookingId) });
  const usersQuery = useQuery({ queryKey: ["users", "assignments"], queryFn: () => listUsers({ page: 1, page_size: 100 }) });
  const booking = bookingQuery.data;
  const scheduleMutation = useMutation({
    mutationFn: (values: ScheduleFormValues) => createSchedule({
      ...values,
      booking_id: bookingId!,
      scheduled_start: values.scheduled_start!.toISOString(),
      scheduled_end: values.scheduled_end!.toISOString()
    }),
    onSuccess: async () => {
      message.success("Shoot scheduled");
      setIsScheduleOpen(false);
      scheduleForm.resetFields();
      await queryClient.invalidateQueries({ queryKey: ["bookings", bookingId] });
    }
  });
  const assignmentMutation = useMutation({
    mutationFn: createAssignment,
    onSuccess: async () => {
      message.success("Photographer assigned");
      setAssignmentScheduleId(null);
      assignmentForm.resetFields();
      await queryClient.invalidateQueries({ queryKey: ["bookings", bookingId] });
    }
  });
  const schedules = booking?.items.flatMap((item) => item.schedules ?? []) ?? [];
  const editable = canManageBookings(roleNames) && booking?.booking_status !== "CANCELLED";

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>{booking?.booking_number ?? "Booking"}</Typography.Title>
          <Typography.Text type="secondary">{booking?.family?.primary_contact_name ?? "Loading booking"}</Typography.Text>
        </div>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/bookings")}>Back</Button>
      </div>
      <Card loading={bookingQuery.isLoading} title="Booking Summary">
        {booking && (
          <Descriptions bordered size="small" column={{ xs: 1, md: 2, xl: 3 }}>
            <Descriptions.Item label="Status"><Tag>{labelFromEnum(booking.booking_status)}</Tag></Descriptions.Item>
            <Descriptions.Item label="Family">{booking.family?.primary_contact_name}</Descriptions.Item>
            <Descriptions.Item label="Phone">{booking.family?.primary_contact_phone}</Descriptions.Item>
            <Descriptions.Item label="Opportunity">{booking.opportunity ? labelFromEnum(booking.opportunity.opportunity_type) : "-"}</Descriptions.Item>
            <Descriptions.Item label="Total">₹{Number(booking.total_amount).toLocaleString("en-IN")}</Descriptions.Item>
            <Descriptions.Item label="Balance">₹{Number(booking.balance_amount).toLocaleString("en-IN")}</Descriptions.Item>
          </Descriptions>
        )}
      </Card>
      <Card title="Booking Items" extra={editable ? <Button icon={<PlusOutlined />} onClick={() => setIsScheduleOpen(true)}>Schedule Shoot</Button> : null}>
        <List dataSource={booking?.items ?? []} renderItem={(item) => (
          <List.Item>
            <List.Item.Meta title={`${item.package?.name ?? "Package"} · ${labelFromEnum(item.service_type)}`} description={`Final amount ₹${Number(item.final_amount).toLocaleString("en-IN")}`} />
            <Tag>{labelFromEnum(item.status)}</Tag>
          </List.Item>
        )} />
      </Card>
      <Card title="Schedules">
        <List dataSource={schedules} locale={{ emptyText: "No schedules yet" }} renderItem={(schedule) => (
          <List.Item actions={canAssignPhotographers(roleNames) ? [<Button key="assign" onClick={() => setAssignmentScheduleId(schedule.id)}>Assign</Button>] : []}>
            <List.Item.Meta title={`${dayjs(schedule.scheduled_start).format("DD MMM YYYY, h:mm A")} · ${schedule.location}`} description={labelFromEnum(schedule.shoot_status)} />
          </List.Item>
        )} />
      </Card>
      <Modal title="Schedule Shoot" open={isScheduleOpen} onCancel={() => setIsScheduleOpen(false)} onOk={() => scheduleForm.submit()} confirmLoading={scheduleMutation.isPending}>
        <Form form={scheduleForm} layout="vertical" requiredMark={false} initialValues={{ shoot_status: "SCHEDULED" }} onFinish={(values) => scheduleMutation.mutate(values)}>
          <Form.Item label="Booking Item" name="booking_item_id" rules={[{ required: true }]}><Select options={(booking?.items ?? []).map((item) => ({ value: item.id, label: `${item.package?.name ?? item.service_type} · ${labelFromEnum(item.service_type)}` }))} /></Form.Item>
          <Form.Item label="Start" name="scheduled_start" rules={[{ required: true }]}><DatePicker showTime className="full-width-control" /></Form.Item>
          <Form.Item label="End" name="scheduled_end" rules={[{ required: true }]}><DatePicker showTime className="full-width-control" /></Form.Item>
          <Form.Item label="Location" name="location" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item label="Status" name="shoot_status"><Select options={shootStatuses.map((value) => ({ value, label: labelFromEnum(value) }))} /></Form.Item>
          <Form.Item label="Notes" name="notes"><Input.TextArea rows={3} /></Form.Item>
        </Form>
      </Modal>
      <Modal title="Assign Photographer" open={Boolean(assignmentScheduleId)} onCancel={() => setAssignmentScheduleId(null)} onOk={() => assignmentForm.submit()} confirmLoading={assignmentMutation.isPending}>
        <Form form={assignmentForm} layout="vertical" requiredMark={false} initialValues={{ shoot_schedule_id: assignmentScheduleId, role: "LEAD_PHOTOGRAPHER" }} onFinish={(values) => assignmentMutation.mutate({ ...values, shoot_schedule_id: assignmentScheduleId! })}>
          <Form.Item label="User" name="user_id" rules={[{ required: true }]}><Select options={(usersQuery.data?.items ?? []).map((item) => ({ value: item.id, label: `${item.first_name} ${item.last_name}` }))} /></Form.Item>
          <Form.Item label="Role" name="role"><Select options={assignmentRoles.map((value) => ({ value, label: labelFromEnum(value) }))} /></Form.Item>
        </Form>
      </Modal>
    </Space>
  );
}
