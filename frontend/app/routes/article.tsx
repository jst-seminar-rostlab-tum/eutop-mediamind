import { ArticlePage } from "~/pages/article/article";
import { useParams } from "react-router";
import { getArticle } from "~/pages/article/article-mock-data";

export default function Article() {
  const { searchProfileId, matchId } = useParams();

  if (!searchProfileId || !matchId) {
    return <div>Missing parameters!</div>;
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
