import type { components, paths } from "./api-types-v1";

export type MediamindUser = components["schemas"]["UserEntity"];

export type Profile = components["schemas"]["SearchProfileDetailResponse"];

export type Subscription = components["schemas"]["SubscriptionSummary"];

export type ProfileUpdate = components["schemas"]["SearchProfileUpdateRequest"];

export type ProfileCreate = components["schemas"]["SearchProfileCreateRequest"];

export type MatchesResponse =
  paths["/api/v1/search-profiles/{search_profile_id}/matches"]["post"]["responses"]["200"]["content"]["application/json"];
