import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "~/components/ui/accordion";
import { capitalize } from "lodash-es";
import { Badge } from "~/components/ui/badge";
import { useTranslation } from "react-i18next";

interface EntityData {
  entities: { [key: string]: unknown };
}

export function ArticleEntities({ entities }: EntityData) {
  const { t } = useTranslation();

  function isStringArray(value: unknown): value is string[] {
    return (
      Array.isArray(value) && value.every((item) => typeof item === "string")
    );
  }

  return (
    <div className=" p-4 border rounded-lg">
      <span className="font-bold ">{t("article-page.entities")}</span>
      <p className={"text-sm text-gray-400"}>
        {t("article-page.entities_text")}
      </p>
      <Accordion type="multiple" className="w-full">
        {Object.entries(entities).map(
          ([key, values]) =>
            isStringArray(values) && (
              <AccordionItem key={key} value={key}>
                <AccordionTrigger>
                  <div className={"flex gap-2"}>
                    <text>{capitalize(key)}</text>
                    <div
                      className={
                        "rounded-sm bg-gray-100 px-1.5 flex items-center justify-center"
                      }
                    >
                      {values.length}
                    </div>
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  {values.length > 0 ? (
                    key == "citation" ? (
                      <div>
                        <div className={"space-y-2 "}>
                          {values.map((item, index) => (
                            <div key={index} className="relative pl-8">
                              <span className="absolute left-0 top-0 font-medium text-gray-600 text-sm">
                                [{index + 1}]
                              </span>
                              <div className="text-sm leading-relaxed text-gray-800">
                                {item}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div className="flex flex-wrap gap-2">
                        {values.map((item, index) => (
                          <Badge key={index} className="text-sm bg-gray-800">
                            {item}
                          </Badge>
                        ))}
                      </div>
                    )
                  ) : (
                    <p className="text-muted-foreground">
                      No items in this category.
                    </p>
                  )}
                </AccordionContent>
              </AccordionItem>
            ),
        )}
      </Accordion>
    </div>
  );
}
