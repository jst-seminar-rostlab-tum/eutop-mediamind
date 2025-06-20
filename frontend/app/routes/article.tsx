import { ArticlePage } from "~/pages/article/article";
import { useParams } from "react-router";
import { getArticle } from "~/pages/article/article-mock-data";
import { ErrorPage } from "~/pages/error/error";

export default function Article() {
  const { searchProfileId, matchId } = useParams();

  if (!searchProfileId || !matchId) {
    return <ErrorPage />;
  }

  const article = getArticle();

  return (
    <ArticlePage
      searchProfileId={searchProfileId}
      matchId={matchId}
      article={article}
      searchProfileName={article.profile.name}
    />
  );
}
