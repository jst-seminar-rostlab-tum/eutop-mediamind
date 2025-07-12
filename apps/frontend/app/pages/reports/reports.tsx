import { ReportCard } from "~/custom-components/reports/report-card";
import { ReportCardSkeleton } from "~/custom-components/reports/report-card-skeleton";
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
import React, { useState, useMemo } from "react";
import { useTranslation } from "react-i18next";
import Text from "~/custom-components/text";
import { useQuery } from "../../../types/api";
import { ErrorPage } from "~/pages/error/error";
import "./reports.css";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "~/components/ui/pagination";
import { ReportFilterBar } from "~/custom-components/reports/reports-filter-bar";
import { BreadcrumbSkeleton } from "~/custom-components/breadcrumb-skeleton";

export function ReportsPage() {
  const { searchProfileId } = useParams();
  const { t } = useTranslation();

  const [currentPage, setCurrentPage] = useState(1);
  const [languageFilter, setLanguageFilter] = useState<string>("");
  const itemsPerPage = 30;

  const { data: profile, isLoading: profileLoading } = useQuery(
    "/api/v1/search-profiles/{search_profile_id}",
    {
      params: { path: { search_profile_id: searchProfileId || "" } },
    },
  );

  const { data: reports, isLoading } = useQuery(
    "/api/v1/search-profiles/{search_profile_id}/reports",
    {
      params: { path: { search_profile_id: searchProfileId || "" } },
    },
  );

  const filteredReports = useMemo(() => {
    if (!reports?.reports) return [];

    if (!languageFilter) {
      return reports.reports;
    }
    const langToFilter = languageFilter === "en" ? "en" : "de";
    return reports.reports.filter((report) => report.language === langToFilter);
  }, [reports?.reports, languageFilter]);

  const totalItems = filteredReports.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);

  const currentReports = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filteredReports.slice(startIndex, endIndex);
  }, [filteredReports, currentPage, itemsPerPage]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleLanguageChange = (language: string) => {
    setLanguageFilter(language);
    setCurrentPage(1);
  };

  const handleResetFilters = () => {
    setLanguageFilter("");
    setCurrentPage(1);
  };

  const getPageNumbers = () => {
    const pages = [];
    const maxVisiblePages = 5;

    if (totalPages <= maxVisiblePages) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (currentPage <= 3) {
        pages.push(1, 2, 3, 4, "...", totalPages);
      } else if (currentPage >= totalPages - 2) {
        pages.push(
          1,
          "...",
          totalPages - 3,
          totalPages - 2,
          totalPages - 1,
          totalPages,
        );
      } else {
        pages.push(
          1,
          "...",
          currentPage - 1,
          currentPage,
          currentPage + 1,
          "...",
          totalPages,
        );
      }
    }

    return pages;
  };

  if (!searchProfileId || (!profileLoading && !profile)) {
    return <ErrorPage />;
  }

  const from = totalItems > 0 ? (currentPage - 1) * itemsPerPage + 1 : 0;
  const to = Math.min(currentPage * itemsPerPage, totalItems);

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
            {profileLoading ? (
              <BreadcrumbSkeleton />
            ) : (
              <BreadcrumbLink asChild>
                <Link to={`/search-profile/${searchProfileId}`}>
                  {profile?.name}
                </Link>
              </BreadcrumbLink>
            )}
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>{t("reports.reports")}</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      <Text hierachy={2}>{t("reports.header")}</Text>

      {profileLoading || isLoading ? (
        <>
          <ReportFilterBar
            language={languageFilter}
            onLanguageChange={handleLanguageChange}
            onReset={handleResetFilters}
          />
          <div className="grid-report-cards mt-4">
            {Array.from({ length: 12 }).map((_, index) => (
              <ReportCardSkeleton key={index} />
            ))}
          </div>
        </>
      ) : !reports || !reports.reports || reports.reports.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-muted-foreground">
            {t("reports.no_reports_found")}
          </p>
        </div>
      ) : (
        <>
          <ReportFilterBar
            language={languageFilter}
            onLanguageChange={handleLanguageChange}
            onReset={handleResetFilters}
          />

          {filteredReports.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">
                {t("reports.no_reports_match_filter")}
              </p>
            </div>
          ) : (
            <>
              <div className="grid-report-cards mt-4">
                {currentReports.map((report, index) => (
                  <ReportCard key={report.id || index} report={report} />
                ))}
              </div>

              {totalPages > 1 && (
                <Pagination className="mt-8">
                  <PaginationContent>
                    <PaginationItem>
                      <PaginationPrevious
                        onClick={() =>
                          handlePageChange(Math.max(1, currentPage - 1))
                        }
                        className={
                          currentPage === 1
                            ? "pointer-events-none opacity-50"
                            : "cursor-pointer"
                        }
                      />
                    </PaginationItem>

                    {getPageNumbers().map((page, index) => (
                      <PaginationItem key={index}>
                        {page === "..." ? (
                          <PaginationEllipsis />
                        ) : (
                          <PaginationLink
                            onClick={() => handlePageChange(page as number)}
                            isActive={currentPage === page}
                            className="cursor-pointer"
                          >
                            {page}
                          </PaginationLink>
                        )}
                      </PaginationItem>
                    ))}

                    <PaginationItem>
                      <PaginationNext
                        onClick={() =>
                          handlePageChange(
                            Math.min(totalPages, currentPage + 1),
                          )
                        }
                        className={
                          currentPage === totalPages
                            ? "pointer-events-none opacity-50"
                            : "cursor-pointer"
                        }
                      />
                    </PaginationItem>
                  </PaginationContent>
                </Pagination>
              )}

              <div className="text-sm text-muted-foreground mt-4 text-center">
                {t("reports.pagination", { from, to, total: totalItems })}
              </div>
            </>
          )}
        </>
      )}
    </Layout>
  );
}
