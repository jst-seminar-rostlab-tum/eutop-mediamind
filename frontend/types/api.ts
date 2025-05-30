import createClient from "openapi-fetch";
import { createQueryHook, createMutateHook, createImmutableHook, createInfiniteHook } from "swr-openapi";
import type { paths } from "./schema";
import { isMatch } from "lodash-es";

const client = createClient<paths>({
  baseUrl: "http://localhost:8000",
});

const API_PREFIX = "my-api";

export const useQuery = createQueryHook(client, API_PREFIX);
export const useImmutable = createImmutableHook(client, API_PREFIX);
export const useInfinite = createInfiniteHook(client, API_PREFIX);
export const useMutate = createMutateHook(
  client,
  API_PREFIX,
  isMatch,
);