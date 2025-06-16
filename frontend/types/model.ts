import type { components } from "./api-types-v1";
import type { NewsArticle } from "~/pages/article/article-mock-data";

export type MediamindUser = components["schemas"]["UserEntity"];

export type Profile = components["schemas"]["SearchProfileDetailResponse"];

export type Subscription = components["schemas"]["SubscriptionSummary"];

export type ProfileUpdate = components["schemas"]["SearchProfileUpdateRequest"];

export type ProfileCreate = components["schemas"]["SearchProfileCreateRequest"];

export type Article = NewsArticle; // components["schemas"]["MatchDetailResponse"]
