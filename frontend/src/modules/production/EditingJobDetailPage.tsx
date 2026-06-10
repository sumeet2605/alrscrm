import { ArrowLeftOutlined, CheckOutlined, PlayCircleOutlined, SendOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  App,
  Alert,
  Button,
  Descriptions,
  Form,
  Input,
  InputNumber,
  Modal,
  Select,
  Space,
  Spin,
  Table,
  Tag,
  Typography
} from "antd";
import type { ColumnsType } from "antd/es/table";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  approveEditingJob,
  assignEditingJob,
  getEditingJob,
  markEditingReadyForDelivery,
  rejectEditingJob,
  startEditingJob,
  submitEditingReview,
  updateEditingJob
} from "../../api/editing";
import { listUsers } from "../../api/identity";
import type { EditingReview } from "../../types/editing";
import type { User } from "../../types/identity";
import { editingStatusColor, labelFromEnum, priorityColor } from "./editingOptions";

export function EditingJobDetailPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { message } = App.useApp();
  const [assignOpen, setAssignOpen] = useState(false);
  const [reviewOpen, setReviewOpen] = useState<"approve" | "reject" | null>(null);
  const [assignForm] = Form.useForm<{ assigned_editor_id: string }>();
  const [reviewForm] = Form.useForm<{ review_notes?: string }>();

  const jobQuery = useQuery({
    queryKey: ["editing-job", jobId],
    queryFn: () => getEditingJob(jobId!),
    enabled: Boolean(jobId)
  });
  const usersQuery = useQuery({
    queryKey: ["users", "editors"],
    queryFn: () => listUsers({ page: 1, page_size: 100 })
  });

  const invalidate = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ["editing-job", jobId] }),
      queryClient.invalidateQueries({ queryKey: ["editing-jobs"] }),
      queryClient.invalidateQueries({ queryKey: ["editing-metrics"] })
    ]);
  };

  const actionMutation = useMutation({
    mutationFn: async (action: "start" | "submit" | "ready") => {
      if (action === "start") return startEditingJob(jobId!);
      if (action === "submit") return submitEditingReview(jobId!);
      return markEditingReadyForDelivery(jobId!);
    },
    onSuccess: async () => {
      message.success("Editing job updated");
      await invalidate();
    }
  });
  const completeMutation = useMutation({
    mutationFn: (completed_photo_count: number) =>
      updateEditingJob(jobId!, { completed_photo_count }),
    onSuccess: async () => {
      message.success("Completed count updated");
      await invalidate();
    }
  });
  const assignMutation = useMutation({
    mutationFn: (assigned_editor_id: string) => assignEditingJob(jobId!, { assigned_editor_id }),
    onSuccess: async () => {
      message.success("Editor assigned");
      setAssignOpen(false);
      assignForm.resetFields();
      await invalidate();
    }
  });
  const reviewMutation = useMutation({
    mutationFn: (values: { review_notes?: string }) =>
      reviewOpen === "approve"
        ? approveEditingJob(jobId!, values)
        : rejectEditingJob(jobId!, values),
    onSuccess: async () => {
      message.success(reviewOpen === "approve" ? "Job approved" : "Changes requested");
      setReviewOpen(null);
      reviewForm.resetFields();
      await invalidate();
    }
  });

  const job = jobQuery.data;
  const editorOptions = (usersQuery.data?.items ?? [])
    .filter((user: User) => user.roles.some((role) => role.name === "Editor"))
    .map((user) => ({
      value: user.id,
      label: `${user.first_name} ${user.last_name} · ${user.email}`
    }));

  const reviewColumns: ColumnsType<EditingReview> = [
    { title: "Status", dataIndex: "review_status", render: (value: string) => labelFromEnum(value) },
    { title: "Reviewer", render: (_, review) => review.reviewed_by_user?.email ?? review.reviewed_by_user_id },
    { title: "Notes", dataIndex: "review_notes" },
    { title: "Reviewed At", dataIndex: "reviewed_at" }
  ];

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>{job?.gallery_name ?? "Editing Job"}</Typography.Title>
          <Typography.Text type="secondary">
            {job?.booking_number} · {job?.family_name}
          </Typography.Text>
        </div>
        <Space wrap>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/production/editing")}>
            Back
          </Button>
          <Button onClick={() => setAssignOpen(true)}>Assign Editor</Button>
          <Button
            icon={<PlayCircleOutlined />}
            onClick={() => actionMutation.mutate("start")}
            disabled={!job || job.editing_status === "READY_FOR_DELIVERY"}
          >
            Start
          </Button>
          <Button icon={<SendOutlined />} onClick={() => actionMutation.mutate("submit")}>
            Submit Review
          </Button>
          <Button onClick={() => setReviewOpen("reject")}>Reject</Button>
          <Button type="primary" icon={<CheckOutlined />} onClick={() => setReviewOpen("approve")}>
            Approve
          </Button>
          <Button onClick={() => actionMutation.mutate("ready")}>Ready For Delivery</Button>
        </Space>
      </div>

      {jobQuery.isLoading ? (
        <Spin />
      ) : null}

      {jobQuery.isError ? (
        <Alert
          type="error"
          showIcon
          message="Unable to load editing job"
          description="Return to the queue or refresh the page after checking your connection."
        />
      ) : null}

      {job ? (
        <>
          <Descriptions bordered column={{ xs: 1, md: 3 }}>
            <Descriptions.Item label="Status">
              <Tag color={editingStatusColor(job.editing_status)}>
                {labelFromEnum(job.editing_status)}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Priority">
              <Tag color={priorityColor(job.priority)}>{labelFromEnum(job.priority)}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Due Date">{job.due_date}</Descriptions.Item>
            <Descriptions.Item label="Service">{job.service_type ? labelFromEnum(job.service_type) : "-"}</Descriptions.Item>
            <Descriptions.Item label="Editor">
              {job.assigned_editor
                ? `${job.assigned_editor.first_name} ${job.assigned_editor.last_name}`
                : "Unassigned"}
            </Descriptions.Item>
            <Descriptions.Item label="Photos">
              <Space>
                <InputNumber
                  min={0}
                  max={job.selected_photo_count}
                  value={job.completed_photo_count}
                  onChange={(value) => {
                    if (typeof value === "number") completeMutation.mutate(value);
                  }}
                />
                <Typography.Text>/ {job.selected_photo_count}</Typography.Text>
              </Space>
            </Descriptions.Item>
            <Descriptions.Item label="Started At">{job.started_at ?? "-"}</Descriptions.Item>
            <Descriptions.Item label="Completed At">{job.completed_at ?? "-"}</Descriptions.Item>
            <Descriptions.Item label="Notes">{job.notes ?? "-"}</Descriptions.Item>
          </Descriptions>

          <Table<EditingReview>
            rowKey="id"
            title={() => "Reviews"}
            dataSource={job.reviews}
            pagination={false}
            columns={reviewColumns}
          />
        </>
      ) : null}

      <Modal
        title="Assign Editor"
        open={assignOpen}
        onCancel={() => setAssignOpen(false)}
        onOk={() => assignForm.submit()}
        confirmLoading={assignMutation.isPending}
      >
        <Form form={assignForm} layout="vertical" onFinish={(values) => assignMutation.mutate(values.assigned_editor_id)}>
          <Form.Item name="assigned_editor_id" label="Editor" rules={[{ required: true }]}>
            <Select loading={usersQuery.isLoading} options={editorOptions} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={reviewOpen === "approve" ? "Approve Editing Job" : "Reject Editing Job"}
        open={reviewOpen !== null}
        onCancel={() => setReviewOpen(null)}
        onOk={() => reviewForm.submit()}
        confirmLoading={reviewMutation.isPending}
      >
        <Form form={reviewForm} layout="vertical" onFinish={(values) => reviewMutation.mutate(values)}>
          <Form.Item name="review_notes" label="Review Notes">
            <Input.TextArea rows={4} />
          </Form.Item>
        </Form>
      </Modal>
    </Space>
  );
}
