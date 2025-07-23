import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "~/components/ui/accordion";
import { capitalize } from "lodash-es";
import { Badge } from "~/components/ui/badge";
import { useTranslation } from "react-i18next";

interface LocalizedString {
  [key: string]: string;
}

export type EntityValue = string | LocalizedString;

interface EntityData {
  entities: { [key: string]: EntityValue[] };
}

export function ArticleEntities({ entities }: EntityData) {
  const { t, i18n } = useTranslation();

  function isValidEntityArray(value: unknown): value is EntityValue[] {
    if (!Array.isArray(value)) return false;

    return value.every((item) => {
      if (typeof item === "string") return true;

      if (typeof item === "object" && item !== null) {
        return Object.values(item).every((val) => typeof val === "string");
      }

      return false;
    });
  }

  function getLocalizedValue(value: EntityValue): string {
    if (typeof value === "string") {
      return value;
    }

    const currentLang = i18n.language;
    if (value[currentLang]) {
      return value[currentLang];
    }

    const firstKey = Object.keys(value)[0];
    return firstKey ? value[firstKey] : "";
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
            isValidEntityArray(values) && (
              <AccordionItem key={key} value={key}>
                <AccordionTrigger>
                  <div className={"flex gap-2"}>
                    <p>
                      {t(`article-page.${key}`, {
                        defaultValue: capitalize(key),
                      })}
                    </p>
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
                                {getLocalizedValue(item)}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div className="flex flex-wrap gap-2">
                        {values.map((item, index) => (
                          <Badge key={index} className="text-sm bg-gray-800">
                            {getLocalizedValue(item)}
                          </Badge>
                        ))}
                      </div>
                    )
                  ) : (
                    <p className="text-muted-foreground">
                      {t("article-page.no_entities")}
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
