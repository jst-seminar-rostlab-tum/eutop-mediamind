import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("admin", "routes/admin.tsx"),
  route("dashboard", "routes/dashboard.tsx"),
  route("/search-profile/:searchProfileId/:matchId", "routes/article.tsx"),
  route("error/:code", "routes/error.tsx"),
  route("search-profile/:id", "routes/search-profile.tsx"),
  route("dashboard/breaking", "routes/breaking-news.tsx"),
  route("search-profile/:searchProfileId/reports", "routes/reports.tsx"),
] satisfies RouteConfig;
