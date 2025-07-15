import { useEffect, useState, useMemo } from "react";
import { useQuery } from "types/api";
import Layout from "~/custom-components/layout";
import Text from "~/custom-components/text";
import { DatePicker } from "~/custom-components/date-picker/date-picker";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "~/components/ui/breadcrumb";
import { Link } from "react-router";
import { type ColumnDef } from "@tanstack/react-table";
import type { Stat } from "types/model";
import { DataTable } from "~/custom-components/admin-settings/data-table";
import { format } from "date-fns";
import { Card } from "~/components/ui/card";

export const CrawlerStatsPage = () => {
  const { t } = useTranslation();
  const [startDate, setStartDate] = useState<Date | undefined>(new Date());
  const [endDate, setEndDate] = useState<Date | undefined>(new Date());

  const { data, error } = useQuery("/api/v1/crawler/stats", {
    params: {
      query: {
        date_start: startDate?.toISOString().split("T")[0],
        date_end: endDate?.toISOString().split("T")[0],
      },
    },
  });

  useEffect(() => {
    if (error) {
      toast.error(t("crawler_stats.error"));
    }
  }, [error, t]);

  const columns = useMemo<ColumnDef<Stat>[]>(
    () => [
      {
        accessorKey: "subscription_name",
        header: t("crawler_stats.subscription"),
        enableSorting: true,
      },
      {
        accessorKey: "crawl_date",
        header: t("crawler_stats.date"),
        cell: (info) => format(info.getValue() as Date, "yyyy-MM-dd HH:mm:ss"),
        enableSorting: true,
      },
      {
        accessorKey: "total_successful",
        header: t("crawler_stats.successful"),
        enableSorting: true,
      },
      {
        accessorKey: "total_attempted",
        header: t("crawler_stats.attempted"),
        enableSorting: true,
      },
      {
        accessorFn: (row) => row.total_attempted - row.total_successful,
        id: "total_failed",
        header: t("crawler_stats.failed"),
        enableSorting: true,
        cell: (info) => (
          <span className={info.getValue() ? "text-destructive" : ""}>
            {info.getValue() ? (info.getValue() as string) : ""}
          </span>
        ),
      },
      {
        accessorKey: "notes",
        header: t("crawler_stats.notes"),
        cell: (info) => info.getValue() ?? "",
        enableSorting: false,
        meta: {
          className: "max-w-[400px] whitespace-normal break-words",
        },
      },
    ],
    [t],
  );

  return (
    <Layout noOverflow={true}>
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link to="/dashboard">{t("breadcrumb_home")}</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>{t("crawler_stats.title")}</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
      <Text hierachy={2}>{t("crawler_stats.title")}</Text>

      <Card className="gap-4 p-6 overflow-hidden h-full mb-20">
        <DatePicker
          startDate={startDate}
          endDate={endDate}
          setStartDate={setStartDate}
          setEndDate={setEndDate}
        />
        <DataTable
          columns={columns}
          data={data?.stats ?? []}
          searchField="subscription_name"
        />
      </Card>
    </Layout>
  );
};
