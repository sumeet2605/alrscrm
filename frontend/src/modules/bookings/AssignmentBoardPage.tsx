import { useQuery } from "@tanstack/react-query";
import { Card, Col, List, Row, Space, Tag, Typography } from "antd";
import dayjs from "dayjs";

import { listAssignments, listSchedules } from "../../api/bookings";
import { labelFromEnum } from "./bookingOptions";

export function AssignmentBoardPage() {
  const schedulesQuery = useQuery({ queryKey: ["schedules", "assignment-board"], queryFn: () => listSchedules({ page: 1, page_size: 100 }) });
  const assignmentsQuery = useQuery({ queryKey: ["assignments"], queryFn: () => listAssignments() });
  const schedules = schedulesQuery.data?.items ?? [];
  const assignedIds = new Set(assignmentsQuery.data?.map((item) => item.shoot_schedule_id) ?? []);
  const unassigned = schedules.filter((item) => !assignedIds.has(item.id));
  const upcoming = schedules.filter((item) => dayjs(item.scheduled_start).isAfter(dayjs()));
  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Photographer Assignment Board</Typography.Title>
          <Typography.Text type="secondary">Upcoming, assigned, and unassigned shoots.</Typography.Text>
        </div>
      </div>
      <Row gutter={[16, 16]}>
        <BoardColumn title="Upcoming Shoots" items={upcoming.map((item) => `${dayjs(item.scheduled_start).format("DD MMM")} · ${item.location}`)} />
        <BoardColumn title="Assigned Shoots" items={(assignmentsQuery.data ?? []).map((item) => `${item.user?.first_name ?? "Photographer"} · ${labelFromEnum(item.role)}`)} />
        <BoardColumn title="Unassigned Shoots" items={unassigned.map((item) => `${dayjs(item.scheduled_start).format("DD MMM")} · ${item.location}`)} />
      </Row>
    </Space>
  );
}

function BoardColumn({ title, items }: { title: string; items: string[] }) {
  return (
    <Col xs={24} lg={8}>
      <Card title={<Space>{title}<Tag>{items.length}</Tag></Space>}>
        <List dataSource={items} locale={{ emptyText: "No items" }} renderItem={(item) => <List.Item>{item}</List.Item>} />
      </Card>
    </Col>
  );
}
