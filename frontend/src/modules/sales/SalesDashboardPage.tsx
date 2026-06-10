import { CalendarOutlined, CheckCircleOutlined, CloseCircleOutlined, DollarOutlined, PercentageOutlined, PlusOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button, Card, Col, List, Row, Space, Statistic, Tabs, Tag, Typography, message } from "antd";
import dayjs from "dayjs";
import { useNavigate } from "react-router-dom";

import { getPipeline, getSalesMetrics, listFollowUps, listLostReasons, updateOpportunity } from "../../api/sales";
import { useAuth } from "../../contexts/AuthContext";
import type { Opportunity, OpportunityStage } from "../../types/sales";
import { canWriteSales, labelFromEnum, opportunityStages, stageColor } from "./salesOptions";

export function SalesDashboardPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const roleNames = user?.roles.map((role) => role.name) ?? [];
  const pipelineQuery = useQuery({ queryKey: ["sales", "pipeline"], queryFn: getPipeline });
  const metricsQuery = useQuery({ queryKey: ["sales", "metrics"], queryFn: getSalesMetrics });
  const today = dayjs().format("YYYY-MM-DD");
  const todayFollowUps = useQuery({
    queryKey: ["followups", "today"],
    queryFn: () => listFollowUps({ page: 1, page_size: 5, due_from: today, due_to: today })
  });
  const upcomingFollowUps = useQuery({
    queryKey: ["followups", "upcoming"],
    queryFn: () =>
      listFollowUps({
        page: 1,
        page_size: 5,
        due_from: dayjs().add(1, "day").format("YYYY-MM-DD")
      })
  });
  const missedFollowUps = useQuery({
    queryKey: ["followups", "missed"],
    queryFn: () => listFollowUps({ page: 1, page_size: 5, status: "MISSED" })
  });
  const lostReasonsQuery = useQuery({ queryKey: ["lost-reasons"], queryFn: listLostReasons });

  const stageMutation = useMutation({
    mutationFn: ({ id, stage }: { id: string; stage: OpportunityStage }) =>
      updateOpportunity(id, { current_stage: stage }),
    onSuccess: async () => {
      message.success("Opportunity stage updated");
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["sales"] }),
        queryClient.invalidateQueries({ queryKey: ["opportunities"] })
      ]);
    }
  });

  const pipeline = pipelineQuery.data;
  const lostTotal = pipeline?.LOST.length ?? 0;

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Sales Pipeline</Typography.Title>
          <Typography.Text type="secondary">Track opportunities, follow-ups, conversion, and lost reasons.</Typography.Text>
        </div>
        {canWriteSales(roleNames) && (
          <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate("/sales/opportunities/new")}>
            New Opportunity
          </Button>
        )}
      </div>
      <Row gutter={[16, 16]}>
        <Metric title="Open Opportunities" value={metricsQuery.data?.open_opportunities ?? 0} loading={metricsQuery.isLoading} />
        <Metric title="Booked" value={metricsQuery.data?.booked_opportunities ?? 0} loading={metricsQuery.isLoading} icon={<CheckCircleOutlined />} />
        <Metric title="Lost" value={metricsQuery.data?.lost_opportunities ?? 0} loading={metricsQuery.isLoading} icon={<CloseCircleOutlined />} />
        <Metric title="Conversion" value={metricsQuery.data?.conversion_rate ?? 0} suffix="%" loading={metricsQuery.isLoading} icon={<PercentageOutlined />} />
        <Metric title="Pending Follow Ups" value={metricsQuery.data?.pending_followups ?? 0} loading={metricsQuery.isLoading} icon={<CalendarOutlined />} />
        <Metric title="Missed Follow Ups" value={metricsQuery.data?.missed_followups ?? 0} loading={metricsQuery.isLoading} icon={<CalendarOutlined />} />
        <Metric title="Follow Up Compliance" value={metricsQuery.data?.follow_up_compliance ?? 100} suffix="%" loading={metricsQuery.isLoading} icon={<PercentageOutlined />} />
        <Metric title="Avg Opportunity Value" value={metricsQuery.data?.average_opportunity_value ?? 0} prefix="₹" loading={metricsQuery.isLoading} icon={<DollarOutlined />} />
      </Row>
      <Tabs
        items={[
          {
            key: "pipeline",
            label: "Pipeline",
            children: (
              <div className="pipeline-board">
                {opportunityStages.map((stage) => (
                  <div
                    className="pipeline-column"
                    key={stage}
                    onDragOver={(event) => event.preventDefault()}
                    onDrop={(event) => {
                      const id = event.dataTransfer.getData("opportunity-id");
                      if (id && canWriteSales(roleNames)) {
                        stageMutation.mutate({ id, stage });
                      }
                    }}
                  >
                    <div className="pipeline-column-header">
                      <Typography.Text strong>{labelFromEnum(stage)}</Typography.Text>
                      <Tag color={stageColor(stage)}>{pipeline?.[stage]?.length ?? 0}</Tag>
                    </div>
                    <Space direction="vertical" size={10} className="page-stack">
                      {(pipeline?.[stage] ?? []).map((opportunity) => (
                        <OpportunityCard
                          key={opportunity.id}
                          opportunity={opportunity}
                          draggable={canWriteSales(roleNames) && opportunity.current_stage !== "BOOKED"}
                        />
                      ))}
                    </Space>
                  </div>
                ))}
              </div>
            )
          },
          {
            key: "followups",
            label: "Follow Ups",
            children: (
              <Row gutter={[16, 16]}>
                <FollowUpCard title="Today's Follow Ups" items={todayFollowUps.data?.items ?? []} />
                <FollowUpCard title="Upcoming Follow Ups" items={upcomingFollowUps.data?.items ?? []} />
                <FollowUpCard title="Missed Follow Ups" items={missedFollowUps.data?.items ?? []} />
              </Row>
            )
          },
          {
            key: "lost",
            label: "Lost Analytics",
            children: (
              <Card title="Lost Reasons">
                <List
                  dataSource={lostReasonsQuery.data ?? []}
                  renderItem={(reason) => {
                    const count = (pipeline?.LOST ?? []).filter((item) => item.lost_reason_id === reason.id).length;
                    const percentage = lostTotal ? Math.round((count / lostTotal) * 100) : 0;
                    return (
                      <List.Item>
                        <List.Item.Meta title={reason.name} description={reason.description} />
                        <Tag>{count} · {percentage}%</Tag>
                      </List.Item>
                    );
                  }}
                />
              </Card>
            )
          }
        ]}
      />
    </Space>
  );
}

function Metric({ title, value, loading, icon, suffix, prefix }: { title: string; value: number; loading: boolean; icon?: React.ReactNode; suffix?: string; prefix?: React.ReactNode }) {
  return (
    <Col xs={24} sm={12} lg={6} xl={6}>
      <Card>
        <Statistic title={title} value={value} loading={loading} prefix={prefix ?? icon} suffix={suffix} precision={title.includes("Value") ? 0 : undefined} />
      </Card>
    </Col>
  );
}

function OpportunityCard({ opportunity, draggable }: { opportunity: Opportunity; draggable: boolean }) {
  const navigate = useNavigate();
  return (
    <Card
      size="small"
      className="pipeline-card"
      draggable={draggable}
      onDragStart={(event) => event.dataTransfer.setData("opportunity-id", opportunity.id)}
      onClick={() => navigate(`/sales/opportunities/${opportunity.id}`)}
    >
      <Typography.Text strong>{opportunity.family?.primary_contact_name}</Typography.Text>
      <Typography.Text className="table-subtext">{opportunity.family?.family_code} · {labelFromEnum(opportunity.opportunity_type)}</Typography.Text>
      <Typography.Text className="table-subtext">₹{Number(opportunity.estimated_value).toLocaleString("en-IN")} · {opportunity.probability}%</Typography.Text>
    </Card>
  );
}

function FollowUpCard({ title, items }: { title: string; items: Array<{ id: string; due_date: string; notes?: string | null; status: string }> }) {
  return (
    <Col xs={24} lg={8}>
      <Card title={title}>
        <List
          dataSource={items}
          locale={{ emptyText: "No follow-ups" }}
          renderItem={(item) => (
            <List.Item>
              <List.Item.Meta title={dayjs(item.due_date).format("DD MMM YYYY")} description={item.notes || labelFromEnum(item.status)} />
            </List.Item>
          )}
        />
      </Card>
    </Col>
  );
}
