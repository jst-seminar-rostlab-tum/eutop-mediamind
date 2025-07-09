import { Calendar, FileClock, User } from "lucide-react";

interface ArticleBodyProps {
  title: string;
  content: string;
  published_at: string;
  author?: string;
  imageUrl?: string;
}

const calculateReadingTime = (text: string): string => {
  const averageWordsPerMinute = 225;
  const averageCharactersPerWord = 5;

  const estimatedWords = text.length / averageCharactersPerWord;
  const readingTimeMinutes = estimatedWords / averageWordsPerMinute;

  const roundedMinutes = Math.max(1, Math.round(readingTimeMinutes));

  return `${roundedMinutes} min`;
};

export function ArticleBody({
  title,
  content,
  published_at,
  author,
  imageUrl,
}: ArticleBodyProps) {
  const readingTime = calculateReadingTime(content);

  return (
    <>
      {imageUrl && (
        <img src={imageUrl} className="mt-4 w-full max-h-100 object-cover" />
      )}
      <div className={"space-y-5"}>
        <h2 className={"text-3xl font-bold"}>{title}</h2>
        <div className="flex text-gray-500 text-sm">
          <div className={"flex items-center gap-2"}>
            <Calendar className={"w-4 h-4"} /> {published_at}
          </div>
          {author && (
            <>
              <span className="mx-4">•</span>
              <div className={"flex items-center gap-2"}>
                <User className={"w-4 h-4"} /> {author}
              </div>
            </>
          )}
          <span className="mx-4">•</span>
          <div className={"flex items-center gap-2"}>
            <FileClock className={"w-4 h-4"} />
            {readingTime}
          </div>
        </div>
        <article className={"text-gray-800 whitespace-pre-wrap"}>
          {content}
        </article>
      </div>
    </>
  );
}
