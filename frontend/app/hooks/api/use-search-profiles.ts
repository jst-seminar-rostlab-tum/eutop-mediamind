import { useQuery } from "../../../api/api";
import { useAuthorization } from "../use-authorization";

export function useSearchProfiles() {
  const { authorizationHeaders } = useAuthorization();

  return useQuery("/api/v1/search-profiles", {
    headers: authorizationHeaders,
  });
}
