import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "~/components/ui/breadcrumb";
import React from "react";
import { truncateAtWord } from "~/lib/utils";
import { useTranslation } from "react-i18next";

interface ArticleBreadcrumbProps {
  searchProfileId: string;
  searchProfileName: string;
  articleName: string;
}

export function ArticleBreadcrumb({
  searchProfileId,
  searchProfileName,
  articleName,
}: ArticleBreadcrumbProps) {
  const { t } = useTranslation();
  return (
    <Breadcrumb>
      <BreadcrumbList>
        <BreadcrumbItem>
          <BreadcrumbLink href="/dashboard">
            {t("breadcrumb_home")}
          </BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem>
          <BreadcrumbLink href={`/dashboard/${searchProfileId}`}>
            {searchProfileName}
          </BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem>
          <BreadcrumbPage>{truncateAtWord(articleName, 40)}</BreadcrumbPage>
        </BreadcrumbItem>
      </BreadcrumbList>
    </Breadcrumb>
  );
}
