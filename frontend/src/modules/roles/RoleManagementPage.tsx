import { SafetyCertificateOutlined } from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { Card, Collapse, List, Space, Tag, Typography } from "antd";

import { listRoles } from "../../api/identity";

export function RoleManagementPage() {
  const rolesQuery = useQuery({ queryKey: ["roles"], queryFn: listRoles });

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Roles</Typography.Title>
          <Typography.Text type="secondary">Review role hierarchy and assigned permissions.</Typography.Text>
        </div>
      </div>
      <Card>
        <List
          loading={rolesQuery.isLoading}
          dataSource={rolesQuery.data ?? []}
          renderItem={(role) => (
            <List.Item>
              <List.Item.Meta
                avatar={<SafetyCertificateOutlined className="role-icon" />}
                title={
                  <Space wrap>
                    <Typography.Text strong>{role.name}</Typography.Text>
                    {role.is_platform ? <Tag color="purple">Platform</Tag> : null}
                    <Tag>Priority {role.priority}</Tag>
                  </Space>
                }
                description={role.description}
              />
              <Collapse
                ghost
                className="permission-collapse"
                items={[
                  {
                    key: role.id,
                    label: `${role.permissions.length} permissions`,
                    children: (
                      <Space wrap>
                        {role.permissions.map((permission) => (
                          <Tag key={permission.id} color="blue">
                            {permission.code}
                          </Tag>
                        ))}
                      </Space>
                    )
                  }
                ]}
              />
            </List.Item>
          )}
        />
      </Card>
    </Space>
  );
}
