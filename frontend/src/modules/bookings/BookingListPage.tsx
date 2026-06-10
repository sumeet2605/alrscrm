import { DeleteOutlined, EyeOutlined, PlusOutlined, SearchOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button, Input, Popconfirm, Select, Space, Table, Tag, Typography, message } from "antd";
import type { TableProps } from "antd";
import dayjs from "dayjs";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { deleteBooking, listBookings } from "../../api/bookings";
import { useAuth } from "../../contexts/AuthContext";
import { useDebouncedValue } from "../../hooks/useDebouncedValue";
import type { Booking, BookingStatus, ServiceType } from "../../types/bookings";
import { bookingStatuses, canManageBookings, labelFromEnum, serviceTypes } from "./bookingOptions";

export function BookingListPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const roleNames = user?.roles.map((role) => role.name) ?? [];
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [bookingStatus, setBookingStatus] = useState<BookingStatus | undefined>();
  const [serviceType, setServiceType] = useState<ServiceType | undefined>();
  const debouncedSearch = useDebouncedValue(search);
  const bookingsQuery = useQuery({
    queryKey: ["bookings", page, debouncedSearch, bookingStatus, serviceType],
    queryFn: () =>
      listBookings({
        page,
        page_size: 10,
        search: debouncedSearch || undefined,
        booking_status: bookingStatus,
        service_type: serviceType
      })
  });
  const deleteMutation = useMutation({
    mutationFn: deleteBooking,
    onSuccess: async () => {
      message.success("Booking deleted");
      await queryClient.invalidateQueries({ queryKey: ["bookings"] });
    }
  });

  const columns: TableProps<Booking>["columns"] = [
    {
      title: "Booking",
      render: (_, item) => (
        <div>
          <Button type="link" onClick={() => navigate(`/bookings/${item.id}`)}>{item.booking_number}</Button>
          <Typography.Text className="table-subtext">{item.family?.primary_contact_name} · {item.family?.family_code}</Typography.Text>
        </div>
      )
    },
    { title: "Status", dataIndex: "booking_status", render: (value) => <Tag>{labelFromEnum(value)}</Tag> },
    { title: "Total", dataIndex: "total_amount", render: (value) => `₹${Number(value).toLocaleString("en-IN")}` },
    { title: "Balance", dataIndex: "balance_amount", render: (value) => `₹${Number(value).toLocaleString("en-IN")}` },
    { title: "Date", dataIndex: "booking_date", render: (value) => dayjs(value).format("DD MMM YYYY") },
    {
      title: "Actions",
      width: 120,
      render: (_, item) => (
        <Space>
          <Button icon={<EyeOutlined />} onClick={() => navigate(`/bookings/${item.id}`)} />
          {canManageBookings(roleNames) && item.booking_status !== "CANCELLED" && (
            <Popconfirm title="Delete booking?" okText="Delete" okButtonProps={{ danger: true }} onConfirm={() => deleteMutation.mutate(item.id)}>
              <Button danger icon={<DeleteOutlined />} />
            </Popconfirm>
          )}
        </Space>
      )
    }
  ];

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Bookings</Typography.Title>
          <Typography.Text type="secondary">Track confirmed bookings, value, schedules, and assignments.</Typography.Text>
        </div>
        {canManageBookings(roleNames) && <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate("/bookings/new")}>New Booking</Button>}
      </div>
      <div className="sales-toolbar">
        <Input prefix={<SearchOutlined />} placeholder="Search booking, family, phone, or code" value={search} onChange={(event) => { setPage(1); setSearch(event.target.value); }} allowClear />
        <Select placeholder="Status" value={bookingStatus} onChange={(value) => { setPage(1); setBookingStatus(value); }} allowClear options={bookingStatuses.map((value) => ({ value, label: labelFromEnum(value) }))} />
        <Select placeholder="Service" value={serviceType} onChange={(value) => { setPage(1); setServiceType(value); }} allowClear options={serviceTypes.map((value) => ({ value, label: labelFromEnum(value) }))} />
      </div>
      <Table rowKey="id" loading={bookingsQuery.isLoading} dataSource={bookingsQuery.data?.items ?? []} columns={columns} pagination={{ current: page, pageSize: bookingsQuery.data?.meta.page_size ?? 10, total: bookingsQuery.data?.meta.total ?? 0, onChange: setPage }} />
    </Space>
  );
}
