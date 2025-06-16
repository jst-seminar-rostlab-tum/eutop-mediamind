import { Calendar, FileClock, User } from "lucide-react";

interface ArticleBodyProps {
  title: string;
  content: string;
  published_at: string;
  author: string;
}

export function ArticleBody({
  title,
  content,
  published_at,
  author,
}: ArticleBodyProps) {
  const calculateReadingTime = (text: string): string => {
    const averageWordsPerMinute = 225;
    const averageCharactersPerWord = 5;

    const estimatedWords = text.length / averageCharactersPerWord;
    const readingTimeMinutes = estimatedWords / averageWordsPerMinute;

    const roundedMinutes = Math.max(1, Math.round(readingTimeMinutes));

    return `${roundedMinutes} min`;
  };

  const readingTime = calculateReadingTime(content);

  return (
    <div className={"space-y-5"}>
      <h2 className={"text-3xl font-bold"}>{title}</h2>
      <div className="flex text-gray-500 text-sm">
        <div className={"flex items-center gap-2"}>
          <Calendar className={"w-4 h-4"} /> {published_at}
        </div>
        <span className="mx-4">•</span>
        <div className={"flex items-center gap-2"}>
          <User className={"w-4 h-4"} /> {author}
        </div>
        <span className="mx-4">•</span>
        <div className={"flex items-center gap-2"}>
          <FileClock className={"w-4 h-4"} />
          {readingTime}
        </div>
      </div>
      <p className={"text-gray-800"}>{content}</p>
    </div>
  );
}
