import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("/welcome", "pages/welcome/welcome.tsx"),
  route("/admin", "pages/admin/admin.tsx"),
] satisfies RouteConfig;
