import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "~/components/ui/carousel";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "~/components/ui/accordion";
import { BellRing } from "lucide-react";

type NewsItem = {
  title: string;
  description: string;
};

type Props = {
  breakingNews: NewsItem[];
};

export function BreakingNews({ breakingNews }: Props) {
  return (
    <div className="flex justify-center my-6">
      <Carousel className="w-full max-w-[85%] mx-auto">
        <CarouselContent>
          {breakingNews.map((item, index) => (
            <CarouselItem key={index} className="basis-1/3 ">
              <Card className="gap-1 pb-4">
                <CardHeader className="mt-1">
                  <CardDescription className="flex gap-2 items-center mb-2">
                    <BellRing size={18} />
                    Breaking News
                  </CardDescription>
                  <CardTitle className="mt-1">{item.title}</CardTitle>
                </CardHeader>
                <CardContent className="flex-grow">
                  <Accordion type="single" collapsible>
                    <AccordionItem value="item-1">
                      <AccordionTrigger className="text-blue-400 mt-1">
                        Show more ...
                      </AccordionTrigger>
                      <AccordionContent className="text-base text-gray-800 leading-relaxed text-justify">
                        {item.description}
                      </AccordionContent>
                    </AccordionItem>
                  </Accordion>
                </CardContent>
              </Card>
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselPrevious />
        <CarouselNext />
      </Carousel>
    </div>
  );
}
