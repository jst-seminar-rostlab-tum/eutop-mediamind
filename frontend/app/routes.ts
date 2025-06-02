import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("/error/:code", "routes/error.tsx"),
] satisfies RouteConfig;
