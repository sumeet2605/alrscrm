import { ArrowLeftOutlined, EditOutlined } from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { Button, Card, Descriptions, Empty, List, Space, Tag, Timeline, Typography } from "antd";
import dayjs from "dayjs";
import { useNavigate, useParams } from "react-router-dom";

import { getFamily } from "../../api/families";
import { useAuth } from "../../contexts/AuthContext";
import { canWriteFamilies, familyStatusColor, labelFromEnum } from "./familyOptions";

export function FamilyDetailsPage() {
  const { familyId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const roleNames = user?.roles.map((role) => role.name) ?? [];
  const familyQuery = useQuery({
    queryKey: ["families", familyId],
    queryFn: () => getFamily(familyId!),
    enabled: Boolean(familyId)
  });
  const family = familyQuery.data;

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>{family?.family_code ?? "Family"}</Typography.Title>
          <Typography.Text type="secondary">{family?.primary_contact_name ?? "Loading family profile"}</Typography.Text>
        </div>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/families")}>
            Back
          </Button>
          {family && canWriteFamilies(roleNames) && (
            <Button type="primary" icon={<EditOutlined />} onClick={() => navigate(`/families/${family.id}/edit`)}>
              Edit
            </Button>
          )}
        </Space>
      </div>
      <Card loading={familyQuery.isLoading} title="Profile Summary">
        {family && (
          <Descriptions column={{ xs: 1, md: 2, xl: 3 }} bordered size="small">
            <Descriptions.Item label="Status">
              <Tag color={familyStatusColor(family.status)}>{labelFromEnum(family.status)}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Source">{labelFromEnum(family.source)}</Descriptions.Item>
            <Descriptions.Item label="Primary Phone">{family.primary_contact_phone}</Descriptions.Item>
            <Descriptions.Item label="Primary Email">{family.primary_contact_email || "-"}</Descriptions.Item>
            <Descriptions.Item label="Partner">{family.partner_name || "-"}</Descriptions.Item>
            <Descriptions.Item label="Partner Phone">{family.partner_phone || "-"}</Descriptions.Item>
            <Descriptions.Item label="City">{family.city || "-"}</Descriptions.Item>
            <Descriptions.Item label="Expected Delivery">
              {family.expected_delivery_date ? dayjs(family.expected_delivery_date).format("DD MMM YYYY") : "-"}
            </Descriptions.Item>
            <Descriptions.Item label="Created">{dayjs(family.created_at).format("DD MMM YYYY")}</Descriptions.Item>
          </Descriptions>
        )}
      </Card>
      <div className="details-grid">
        <Card title="Family Members">
          {family?.members.length ? (
            <List
              dataSource={family.members}
              renderItem={(member) => (
                <List.Item>
                  <List.Item.Meta
                    title={member.name}
                    description={`${labelFromEnum(member.relationship)}${member.date_of_birth ? ` · ${dayjs(member.date_of_birth).format("DD MMM YYYY")}` : ""}`}
                  />
                </List.Item>
              )}
            />
          ) : (
            <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No members recorded" />
          )}
        </Card>
        <Card title="Address">
          {family?.address ? (
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Line 1">{family.address.address_line_1}</Descriptions.Item>
              <Descriptions.Item label="Line 2">{family.address.address_line_2 || "-"}</Descriptions.Item>
              <Descriptions.Item label="City">{family.address.city}</Descriptions.Item>
              <Descriptions.Item label="State">{family.address.state}</Descriptions.Item>
              <Descriptions.Item label="Country">{family.address.country}</Descriptions.Item>
              <Descriptions.Item label="Postal Code">{family.address.postal_code}</Descriptions.Item>
            </Descriptions>
          ) : (
            <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No address recorded" />
          )}
        </Card>
      </div>
      <div className="details-grid">
        <Card title="Service Interests">
          {family?.service_interests.length ? (
            <List
              dataSource={family.service_interests}
              renderItem={(interest) => (
                <List.Item>
                  <List.Item.Meta
                    title={labelFromEnum(interest.service_type)}
                    description={`Priority ${interest.priority}${interest.notes ? ` · ${interest.notes}` : ""}`}
                  />
                </List.Item>
              )}
            />
          ) : (
            <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No service interests recorded" />
          )}
        </Card>
        <Card title="Activity Timeline">
          {family ? (
            <Timeline
              items={[
                { children: `Created ${dayjs(family.created_at).format("DD MMM YYYY, h:mm A")}` },
                { children: `Last updated ${dayjs(family.updated_at).format("DD MMM YYYY, h:mm A")}` }
              ]}
            />
          ) : null}
        </Card>
      </div>
    </Space>
  );
}
