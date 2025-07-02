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
import { Link } from "react-router";

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
          <BreadcrumbLink asChild>
            <Link to="/dashboard">{t("breadcrumb_home")}</Link>
          </BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem>
          <BreadcrumbLink asChild>
            <Link to={`/dashboard/${searchProfileId}`}>
              {searchProfileName}
            </Link>
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
