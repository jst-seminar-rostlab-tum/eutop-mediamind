import createClient from "openapi-fetch";
import { createQueryHook } from "swr-openapi";
import type { paths } from "./api-types-v1";

export const BASE_URL =
  import.meta.env.BACKEND_URL ?? "http://localhost:8000/api/v1";

const client = createClient<paths>({
  baseUrl: BASE_URL,
});

const useQuery = createQueryHook(client, "my-api"); // eslint-disable-line @typescript-eslint/no-unused-vars
