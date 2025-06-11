import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { BellRing, ChevronRight } from "lucide-react";
import { ScrollArea, ScrollBar } from "~/components/ui/scroll-area";
import { Button } from "~/components/ui/button";
import { Link } from "react-router";

type NewsItem = {
  title: string;
  description: string;
};

type Props = {
  breakingNews: NewsItem[];
};

function truncateAtWord(text: string, maxLength: number) {
  if (text.length <= maxLength) return text;
  const truncated = text.slice(0, maxLength);
  return truncated.slice(0, truncated.lastIndexOf(" ")) + "…";
}

export function BreakingNews({ breakingNews }: Props) {
  return (
    <div className="flex justify-center my-4">
      <ScrollArea className="w-[100%]">
        <div className="flex w-full mb-6 mt-2 gap-4">
          {breakingNews.map((item, index) => (
            <Card key={index} className="gap-1 pb-3 w-[350px]">
              <CardHeader>
                <CardDescription className="flex gap-2 items-center mb-2 text-blue-600">
                  <BellRing size={18} />
                  Breaking News
                </CardDescription>
                <CardTitle className="mb-3">{item.title}</CardTitle>
              </CardHeader>
              <CardContent className="flex-grow">
                {truncateAtWord(item.description, 70)}
              </CardContent>
              <div className="flex justify-start mx-2 mb-0">
                <Link to="/articlepage">
                  <Button
                    variant={"ghost"}
                    className="ml-1 text-blue-500 items-center"
                  >
                    Read more
                    <ChevronRight />
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
          <ScrollBar orientation="horizontal" />
        </div>
      </ScrollArea>
    </div>
  );
}
