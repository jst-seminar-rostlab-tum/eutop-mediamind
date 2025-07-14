import { Calendar, FileClock, User } from "lucide-react";
import ReactMarkdown from "react-markdown";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "~/components/ui/carousel";

interface ArticleBodyProps {
  title: string;
  content: string;
  published_at: string;
  author?: string;
  image_urls: string[];
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
  image_urls,
}: ArticleBodyProps) {
  const readingTime = calculateReadingTime(content);

  return (
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
      {image_urls.length > 0 && (
        <Carousel className="w-full">
          <CarouselContent className="">
            {image_urls.map((image_url, index) => (
              <CarouselItem key={index}>
                <div key={index}>
                  <img
                    src={image_url}
                    alt={`Article image ${index + 1}`}
                    className="w-full h-auto rounded-lg shadow-sm"
                    loading="lazy"
                  />
                </div>
              </CarouselItem>
            ))}
          </CarouselContent>
          <CarouselPrevious />
          <CarouselNext />
        </Carousel>
      )}
      <section className={"markdown"}>
        <ReactMarkdown>{content}</ReactMarkdown>
      </section>
    </div>
  );
}
