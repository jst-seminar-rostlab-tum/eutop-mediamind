interface ArticleBodyProps {
  title: string;
  content: string;
  published_at: string;
}

export function ArticleBody({
  title,
  content,
  published_at,
}: ArticleBodyProps) {
  return (
    <div className={"space-y-3"}>
      <h2 className={"text-3xl font-bold"}>{title}</h2>
      <p className={"text-gray-500 text-sm"}>{published_at}</p>
      <p className={"text-gray-700"}>{content}</p>
    </div>
  );
}
