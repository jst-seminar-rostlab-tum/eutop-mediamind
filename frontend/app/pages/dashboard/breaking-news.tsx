import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { BellRing, ChevronRight, Newspaper } from "lucide-react";
import { ScrollArea, ScrollBar } from "~/components/ui/scroll-area";
import { Button } from "~/components/ui/button";
import { Link } from "react-router";
import { truncateAtWord } from "~/lib/utils";
import { useTranslation } from "react-i18next";

type NewsItem = {
  title: string;
  description: string;
};

type Props = {
  breakingNews: NewsItem[];
};

export function BreakingNews({ breakingNews }: Props) {
  const { t } = useTranslation();

  return (
    <div className="flex justify-center my-4">
      <ScrollArea className="w-[100%]">
        <div className="flex w-full mb-6 mt-2 gap-4">
          {breakingNews.map((item, index) => (
            <Card key={index} className="gap-1 pb-3 w-[350px] bg-orange-100/50">
              <CardHeader>
                <CardDescription className="flex gap-2 items-center mb-2 text-orange-600">
                  <BellRing size={18} />
                  {t("breaking_news")}
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
                    className="ml-1 text-primary items-center"
                  >
                    <Newspaper />
                    {t("read_more")}
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
