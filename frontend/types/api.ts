import createClient from "openapi-fetch";
import { createQueryHook } from "swr-openapi";
import type { paths } from "./api-types-v1";

const client = createClient<paths>({
  baseUrl: "https://myapi.dev/v1/", // TODO change with proper be url
});

const useQuery = createQueryHook(client, "my-api"); // eslint-disable-line @typescript-eslint/no-unused-vars
