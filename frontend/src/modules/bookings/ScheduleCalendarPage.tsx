import { CalendarOutlined } from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { Card, List, Radio, Space, Tag, Typography } from "antd";
import dayjs from "dayjs";
import { useState } from "react";

import { listSchedules } from "../../api/bookings";
import { labelFromEnum } from "./bookingOptions";

export function ScheduleCalendarPage() {
  const [view, setView] = useState<"month" | "week" | "day">("week");
  const schedulesQuery = useQuery({ queryKey: ["schedules", view], queryFn: () => listSchedules({ page: 1, page_size: 100 }) });
  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Schedule Calendar</Typography.Title>
          <Typography.Text type="secondary">Review month, week, and day shoot schedules.</Typography.Text>
        </div>
        <Radio.Group value={view} onChange={(event) => setView(event.target.value)} options={[{ value: "month", label: "Month" }, { value: "week", label: "Week" }, { value: "day", label: "Day" }]} />
      </div>
      <Card>
        <List dataSource={schedulesQuery.data?.items ?? []} loading={schedulesQuery.isLoading} locale={{ emptyText: "No shoots scheduled" }} renderItem={(item) => (
          <List.Item>
            <List.Item.Meta avatar={<CalendarOutlined />} title={`${dayjs(item.scheduled_start).format("DD MMM YYYY, h:mm A")} · ${item.location}`} description={item.booking?.family?.primary_contact_name ?? item.booking?.booking_number} />
            <Tag>{labelFromEnum(item.shoot_status)}</Tag>
          </List.Item>
        )} />
      </Card>
    </Space>
  );
}
