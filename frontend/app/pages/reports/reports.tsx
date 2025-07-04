import { getReports } from "~/pages/reports/reports-dummy-data";
import { ReportCard } from "~/custom-components/reports/report-card";
import Layout from "~/custom-components/layout";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "~/components/ui/breadcrumb";
import { Link, useParams } from "react-router";
import { truncateAtWord } from "~/lib/utils";
import React from "react";
import { useTranslation } from "react-i18next";
import Text from "~/custom-components/text";
import { useQuery } from "../../../types/api";
import { id } from "date-fns/locale";
import { ErrorPage } from "~/pages/error/error";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "~/components/ui/pagination";
import { ScrollArea } from "~/components/ui/scroll-area";

// interface ReportsPageProps{
//   searchProfileId: string;
//   searchProfileName: string;
// }

export function ReportsPage() {
  const { searchProfileId } = useParams();
  const { t } = useTranslation();

  if (!searchProfileId) {
    return <ErrorPage />;
  }

  const {
    data: profile,
    isLoading,
    error,
    mutate,
  } = useQuery("/api/v1/search-profiles/{search_profile_id}", {
    params: { path: { search_profile_id: searchProfileId } },
  });

  if (!profile) {
    return <ErrorPage />;
  }

  const reports = getReports();
  return (
    <Layout>
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
              <Link to={`/dashboard/${searchProfileId}`}>{profile.name}</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>Reports</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
      <Text hierachy={2}>Report Download Center</Text>
      <div className={"space-y-4"}>
        {reports.reports.map((report) => (
          <ReportCard report={report} />
        ))}
      </div>
    </Layout>
  );
}
