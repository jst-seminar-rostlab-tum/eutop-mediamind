import type { components, paths } from "./api-types-v1";

export type MediamindUser = components["schemas"]["UserEntity"];

export type Profile = components["schemas"]["SearchProfileDetailResponse"];

export type Subscription = components["schemas"]["SubscriptionSummary"];

export type Organization = components["schemas"]["OrganizationResponse"];

export type ProfileUpdate = components["schemas"]["SearchProfileUpdateRequest"];

export type ProfileCreate = components["schemas"]["SearchProfileCreateRequest"];

export type MatchesResponse =
  paths["/api/v1/search-profiles/{search_profile_id}/matches"]["post"]["responses"]["200"]["content"]["application/json"];

export type BreakingNewsItem = components["schemas"]["BreakingNewsItem"];

export type ArticleMatch = components["schemas"]["MatchDetailResponse"];

export type SubscriptionResponse =
  paths["/api/v1/subscriptions/{subscription_id}"]["get"]["responses"]["200"]["content"]["application/json"];
export type Stat = components["schemas"]["CrawlStatsItem"];

export type ProfileReports = components["schemas"]["ReportListResponse"];

export type ReportOverview = components["schemas"]["ReportRead"];

export type Report = components["schemas"]["ReportDetailResponse"];

export type TopicMatch = components["schemas"]["MatchTopicItem"];
