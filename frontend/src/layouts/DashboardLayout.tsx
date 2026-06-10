import {
  ApartmentOutlined,
  AppstoreAddOutlined,
  PictureOutlined,
  ContactsOutlined,
  DashboardOutlined,
  LogoutOutlined,
  ScheduleOutlined,
  RiseOutlined,
  SafetyCertificateOutlined,
  ShopOutlined,
  TeamOutlined,
  ToolOutlined,
  UserOutlined
} from "@ant-design/icons";
import { Avatar, Button, Dropdown, Layout, Menu, Space, Typography, theme } from "antd";
import type { MenuProps } from "antd";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";
import { canAccessPath } from "../routes/routePermissions";

const { Header, Sider, Content } = Layout;

type NavItem = {
  key: string;
  icon?: React.ReactNode;
  label: string;
  children?: NavItem[];
};

const navItems: NavItem[] = [
  { key: "/dashboard", icon: <DashboardOutlined />, label: "Dashboard" },
  { key: "/families", icon: <ContactsOutlined />, label: "Families" },
  { key: "/sales", icon: <RiseOutlined />, label: "Sales" },
  {
    key: "bookings-menu",
    icon: <ShopOutlined />,
    label: "Bookings",
    children: [
      { key: "/bookings", label: "Bookings" },
      { key: "/schedules", label: "Schedules", icon: <ScheduleOutlined /> },
      { key: "/schedules/assignments", label: "Assignments", icon: <TeamOutlined /> },
      { key: "/packages", label: "Package Management", icon: <AppstoreAddOutlined /> },
      { key: "/galleries", label: "Galleries", icon: <PictureOutlined /> }
    ]
  },
  {
    key: "production-menu",
    icon: <ToolOutlined />,
    label: "Production",
    children: [
      { key: "/production/editing", label: "Editing Queue" },
      { key: "/production/editor-dashboard", label: "Editor Dashboard" },
      { key: "/production", label: "Production Dashboard" }
    ]
  },
  { key: "/branches", icon: <ApartmentOutlined />, label: "Branches" },
  { key: "/users", icon: <TeamOutlined />, label: "Users" },
  { key: "/roles", icon: <SafetyCertificateOutlined />, label: "Roles" }
];

function filterNavItems(items: NavItem[], roleNames: string[]): MenuProps["items"] {
  return items
    .map((item) => {
      if (item.children) {
        const children = item.children.filter((child) => canAccessPath(roleNames, child.key));
        return children.length ? { ...item, children } : null;
      }
      return canAccessPath(roleNames, item.key) ? item : null;
    })
    .filter(Boolean) as MenuProps["items"];
}

function selectedMenuPath(pathname: string): string {
  if (pathname.startsWith("/packages")) return "/packages";
  if (pathname.startsWith("/galleries")) return "/galleries";
  if (pathname.startsWith("/production/editing")) return "/production/editing";
  if (pathname.startsWith("/production/editor-dashboard")) return "/production/editor-dashboard";
  if (pathname.startsWith("/production")) return "/production";
  if (pathname.startsWith("/schedules/assignments")) return "/schedules/assignments";
  return `/${pathname.split("/")[1] || "dashboard"}`;
}

export function DashboardLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { token } = theme.useToken();
  const roleNames = user?.roles.map((role) => role.name) ?? [];
  const accessibleItems = filterNavItems(navItems, roleNames);
  const selectedPath = selectedMenuPath(location.pathname);

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
          defaultOpenKeys={["bookings-menu", "production-menu"]}
          selectedKeys={[selectedPath]}
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
