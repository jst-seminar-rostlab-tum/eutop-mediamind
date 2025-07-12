import { ArticlePage } from "~/pages/article/article";
import { useParams } from "react-router";
import { ErrorPage } from "~/pages/error/error";
import { useQuery } from "../../types/api";
import { ArticlePageSkeleton } from "~/custom-components/article/article-page-skeleton";

export default function Article() {
  const { searchProfileId, matchId } = useParams();

  if (!searchProfileId || !matchId) {
    return <ErrorPage />;
  }

  const { data, isLoading, error } = useQuery(
    "/api/v1/search-profiles/{search_profile_id}/article/{match_id}",
    {
      params: {
        path: { search_profile_id: searchProfileId, match_id: matchId },
      },
    },
  );

  if (isLoading) {
    return <ArticlePageSkeleton />;
  }

  if (!data || !data.search_profile || error) {
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
