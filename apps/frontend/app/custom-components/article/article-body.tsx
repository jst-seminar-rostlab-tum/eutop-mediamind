import { Calendar, FileClock, User } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { useState } from "react";
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
  const validImages = image_urls.filter((url) => url && url.trim() !== "");
  const [loadedImages, setLoadedImages] = useState<string[]>([]);

  const handleImageLoad = (imageUrl: string) => {
    setLoadedImages((prev) => [...prev, imageUrl]);
  };

  const handleImageError = (imageUrl: string) => {
    setLoadedImages((prev) => prev.filter((url) => url !== imageUrl));
  };

  const displayImages = validImages.filter((url) => loadedImages.includes(url));

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

      <div style={{ display: "none" }}>
        {validImages.map((image_url, index) => (
          <img
            key={`preload-${index}`}
            src={image_url}
            alt=""
            onLoad={() => handleImageLoad(image_url)}
            onError={() => handleImageError(image_url)}
          />
        ))}
      </div>

      {displayImages.length > 0 && (
        <Carousel className="w-full">
          <CarouselContent className="">
            {displayImages.map((image_url, index) => (
              <CarouselItem key={index}>
                <div>
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
          {displayImages.length > 1 && (
            <>
              <CarouselPrevious />
              <CarouselNext />
            </>
          )}
        </Carousel>
      )}

      <section className={"markdown"}>
        <ReactMarkdown>{content}</ReactMarkdown>
      </section>
    </div>
  );
}
