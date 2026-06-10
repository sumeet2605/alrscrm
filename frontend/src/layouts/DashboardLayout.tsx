import {
  ApartmentOutlined,
  ContactsOutlined,
  DashboardOutlined,
  LogoutOutlined,
  SafetyCertificateOutlined,
  TeamOutlined,
  UserOutlined
} from "@ant-design/icons";
import { Avatar, Button, Dropdown, Layout, Menu, Space, Typography, theme } from "antd";
import type { MenuProps } from "antd";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";
import { canAccessPath } from "../routes/routePermissions";

const { Header, Sider, Content } = Layout;

const navItems = [
  { key: "/dashboard", icon: <DashboardOutlined />, label: "Dashboard" },
  { key: "/families", icon: <ContactsOutlined />, label: "Families" },
  { key: "/branches", icon: <ApartmentOutlined />, label: "Branches" },
  { key: "/users", icon: <TeamOutlined />, label: "Users" },
  { key: "/roles", icon: <SafetyCertificateOutlined />, label: "Roles" }
];

export function DashboardLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { token } = theme.useToken();
  const roleNames = user?.roles.map((role) => role.name) ?? [];
  const accessibleItems = navItems.filter((item) => canAccessPath(roleNames, item.key));

  const menuItems: MenuProps["items"] = [
    {
      key: "profile",
      icon: <UserOutlined />,
      label: `${user?.first_name ?? "User"} ${user?.last_name ?? ""}`.trim()
    },
    { type: "divider" },
    {
      key: "logout",
      icon: <LogoutOutlined />,
      label: "Logout",
      danger: true,
      onClick: async () => {
        await logout();
        navigate("/login", { replace: true });
      }
    }
  ];

  return (
    <Layout className="app-layout">
      <Sider breakpoint="lg" collapsedWidth="0" width={248}>
        <div className="brand-block">
          <div className="brand-mark">A</div>
          <div>
            <Typography.Text className="brand-name">ALRSCRM</Typography.Text>
            <Typography.Text className="brand-subtitle">Studio OS</Typography.Text>
          </div>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[`/${location.pathname.split("/")[1] || "dashboard"}`]}
          items={accessibleItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header className="app-header">
          <div>
            <Typography.Text strong>Family CRM</Typography.Text>
            <Typography.Text type="secondary" className="header-subtitle">
              Studio operations workspace
            </Typography.Text>
          </div>
          <Dropdown menu={{ items: menuItems }} trigger={["click"]}>
            <Button className="profile-button">
              <Space>
                <Avatar size={28} style={{ background: token.colorPrimary }}>
                  {user?.first_name?.[0] ?? "A"}
                </Avatar>
                <span>{user?.email}</span>
              </Space>
            </Button>
          </Dropdown>
        </Header>
        <Content className="app-content">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
