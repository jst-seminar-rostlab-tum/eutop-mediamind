import createClient from "openapi-fetch";
import { createQueryHook } from "swr-openapi";
import type { paths } from "./api-types-v1";

const client = createClient<paths>({
  baseUrl: "https://myapi.dev/v1/", // TODO change with proper be url
});

const useQuery = createQueryHook(client, "my-api"); // eslint-disable-line @typescript-eslint/no-unused-vars

/*
Example:

function MyComponent() {
  const { data, error, isLoading, isValidating, mutate } = useQuery(
    "/api/v1/users"
  );

  if (isLoading || !data) return "Loading...";

  if (error) return `An error occured: ${error.message}`;

  return <div>{ data.title } </div>;
}
*/
