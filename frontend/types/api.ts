import createClient from "openapi-fetch";
import {
  createImmutableHook,
  createInfiniteHook,
  createMutateHook,
  createQueryHook,
} from "swr-openapi";
import type { paths } from "./api-types-v1";
import { isMatch } from "lodash-es";

export const BASE_URL =
  import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8000";

const client = createClient<paths>({
  baseUrl: BASE_URL,
});

export { client };

const API_PREFIX = "api";

export const useQuery = createQueryHook(client, API_PREFIX);
export const useImmutable = createImmutableHook(client, API_PREFIX);
export const useInfinite = createInfiniteHook(client, API_PREFIX);
export const useMutate = createMutateHook(client, API_PREFIX, isMatch);
