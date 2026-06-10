import type { ThemeConfig } from "antd";

export const appTheme: ThemeConfig = {
  token: {
    colorPrimary: "#6A4C93",
    colorSuccess: "#52C41A",
    colorWarning: "#FAAD14",
    colorError: "#FF4D4F",
    colorBgLayout: "#F7F8FC",
    borderRadius: 8,
    fontFamily:
      'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
  },
  components: {
    Layout: {
      headerBg: "#FFFFFF",
      siderBg: "#111827",
      bodyBg: "#F7F8FC"
    },
    Menu: {
      darkItemBg: "#111827",
      darkItemSelectedBg: "#6A4C93"
    },
    Card: {
      borderRadiusLG: 8
    }
  }
};
