import { ArticlePage } from "~/pages/article/article";
import { useParams } from "react-router";
import { ErrorPage } from "~/pages/error/error";
import { useQuery } from "../../types/api";

export default function Article() {
  const { searchProfileId, matchId } = useParams();

  if (!searchProfileId || !matchId) {
    return <ErrorPage />;
  }

  const { data } = useQuery(
    "/api/v1/search-profiles/{search_profile_id}/article/{match_id}",
    {
      params: {
        path: { search_profile_id: searchProfileId, match_id: matchId },
      },
    },
  );

  if (!data || !data.search_profile) {
    return <ErrorPage />;
  }

  return (
    <ArticlePage
      searchProfileId={searchProfileId}
      matchId={matchId}
      article={data}
      searchProfileName={data.search_profile.name}
    />
  );
}
