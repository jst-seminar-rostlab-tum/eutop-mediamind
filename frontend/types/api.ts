import createClient from "openapi-fetch";
import { createQueryHook } from "swr-openapi";
import type { paths } from "./api-types-v1";

export const BASE_URL =
  import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8000";

const client = createClient<paths>({
  baseUrl: BASE_URL,
});

export const useQuery = createQueryHook(client, "my-api");
