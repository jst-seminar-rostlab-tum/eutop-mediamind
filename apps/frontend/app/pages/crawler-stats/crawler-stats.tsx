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
import { CalendarFold, ChartPie } from "lucide-react";
import { Badge } from "~/components/ui/badge";

export const CrawlerStatsPage = () => {
  const { t } = useTranslation();
  const [startDate, setStartDate] = useState<Date | undefined>(new Date());
  const [endDate, setEndDate] = useState<Date | undefined>(new Date());

  const [successRatio, setSuccessRatio] = useState(0);
  const [failureRatio, setFailureRatio] = useState(0);
  const [totalAttempted, setTotalAttempted] = useState(0);
  const [totalSuccessful, setTotalSuccessful] = useState(0);
  const [zeroSuccessful, setZeroSuccessful] = useState(0);
  const [zeroSuccessRatio, setZeroSuccessRatio] = useState(0);

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

  useEffect(() => {
    if (data?.stats?.length) {
      const attempted = data.stats.reduce(
        (sum, stat) => sum + stat.total_attempted,
        0,
      );
      const successful = data.stats.reduce(
        (sum, stat) => sum + stat.total_successful,
        0,
      );
      const zeroSuccessCount =
        data?.stats?.filter((stat) => stat.total_successful === 0).length ?? 0;

      const success = attempted > 0 ? successful / attempted : 0;
      const failure = attempted > 0 ? (attempted - successful) / attempted : 0;
      const zeroSuccessfulRatio =
        attempted > 0 ? zeroSuccessCount / data.stats.length : 0;

      setTotalAttempted(attempted);
      setTotalSuccessful(successful);
      setSuccessRatio(success);
      setFailureRatio(failure);
      setZeroSuccessful(zeroSuccessCount);
      setZeroSuccessRatio(zeroSuccessfulRatio);
    }
  }, [data]);

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
        <div className="flex items-center">
          <CalendarFold className="mr-2" />
          <p className="font-semibold">Timeframe</p>
        </div>
        <DatePicker
          startDate={startDate}
          endDate={endDate}
          setStartDate={setStartDate}
          setEndDate={setEndDate}
        />
        <div className="flex items-center">
          <ChartPie className="mr-2" />
          <p className="font-semibold"> {t("crawler_stats.Statistics")}</p>
        </div>
        <div className="flex gap-4 mb-2">
          <p>{t("crawler_stats.Crawlers") + ":"}</p>
          <Badge>
            {t("crawler_stats.Sum") +
              " " +
              (t("crawler_stats.attempted").toLowerCase() + ": ")}
            {totalAttempted}
          </Badge>
          <Badge className="bg-green-600">
            {t("crawler_stats.Sum") +
              " " +
              (t("crawler_stats.successful").toLowerCase() + ": ")}
            {totalSuccessful} ({(successRatio * 100).toFixed(0)}
            %)
          </Badge>
          <Badge className="bg-red-600">
            {t("crawler_stats.Sum") +
              " " +
              (t("crawler_stats.failed").toLowerCase() + ": ")}
            {totalAttempted - totalSuccessful} (
            {(failureRatio * 100).toFixed(0)}%)
          </Badge>
        </div>
        <div className="flex gap-4 mb-2">
          <p>{t("crawler_stats.Subscriptions") + ":"}</p>
          <Badge>
            {t("crawler_stats.Sum") +
              " " +
              (t("crawler_stats.attempted").toLowerCase() + ": ")}
            {data?.total_count}
          </Badge>
          <Badge className="bg-red-600">
            {t("crawler_stats.Never") +
              " " +
              (t("crawler_stats.successful").toLowerCase() + ": ")}{" "}
            {zeroSuccessful} ({(zeroSuccessRatio * 100).toFixed(0)}%)
          </Badge>
        </div>
        <DataTable
          columns={columns}
          data={data?.stats ?? []}
          searchField="subscription_name"
        />
      </Card>
    </Layout>
  );
};
