import { useEffect, useState, useMemo } from "react";
import { useQuery } from "types/api";
import Layout from "~/custom-components/layout";
import Text from "~/custom-components/text";
import { formatDate } from "~/lib/utils";
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
import {
  useReactTable,
  getCoreRowModel,
  type ColumnDef,
  getSortedRowModel,
  flexRender,
  type SortingState,
} from "@tanstack/react-table";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "~/components/ui/table";
import { Skeleton } from "~/components/ui/skeleton";
import { ArrowDownUp, SortAsc, SortDesc } from "lucide-react";
import type { Stat } from "types/model";

export const CrawlerStatsPage = () => {
  const { t } = useTranslation();
  const [startDate, setStartDate] = useState<Date | undefined>(new Date());
  const [endDate, setEndDate] = useState<Date | undefined>(new Date());
  const [sorting, setSorting] = useState<SortingState>([]);

  const { data, error, isLoading } = useQuery("/api/v1/crawler/stats", {
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
        cell: (info) => formatDate(info.getValue() as string),
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
        accessorKey: "notes",
        header: t("crawler_stats.notes"),
        cell: (info) => info.getValue() ?? "-",
        enableSorting: false,
      },
    ],
    [t],
  );

  const tableData = useMemo<Stat[]>(
    () =>
      data?.stats.map((stat) => ({
        subscription_name: stat.subscription_name,
        crawl_date: stat.crawl_date?.toString() ?? "",
        total_successful: stat.total_successful,
        total_attempted: stat.total_attempted,
        notes: stat.notes ?? "",
      })) ?? [],
    [data],
  );

  const table = useReactTable({
    data: tableData,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  return (
    <Layout>
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink>
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

      <DatePicker
        startDate={startDate}
        endDate={endDate}
        setStartDate={setStartDate}
        setEndDate={setEndDate}
      />
      <div className="space-y-6 p-6">
        <Table>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableHeader key={headerGroup.id}>
              <TableRow>
                {headerGroup.headers.map((header) => {
                  const canSort = header.column.getCanSort();
                  const sortingState = header.column.getIsSorted();
                  return (
                    <TableHead
                      key={header.id}
                      onClick={
                        canSort
                          ? header.column.getToggleSortingHandler()
                          : undefined
                      }
                      className={
                        canSort ? "cursor-pointer select-none" : undefined
                      }
                    >
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext(),
                          )}
                      {sortingState === "asc" ? (
                        <SortAsc className="ms-1 inline size-4" />
                      ) : sortingState === "desc" ? (
                        <SortDesc className="ms-1 inline size-4" />
                      ) : canSort ? (
                        <ArrowDownUp className="ms-1 inline size-4 opacity-50" />
                      ) : null}
                    </TableHead>
                  );
                })}
              </TableRow>
            </TableHeader>
          ))}

          <TableBody>
            {isLoading
              ? Array.from({ length: 5 }).map((_, idx) => (
                  <TableRow key={idx}>
                    {columns.map((col, i) => (
                      <TableCell key={i}>
                        <Skeleton className="h-4 w-full" />
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              : table.getRowModel().rows.map((row) => (
                  <TableRow key={row.id}>
                    {row.getVisibleCells().map((cell) => (
                      <TableCell key={cell.id}>
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext(),
                        )}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
          </TableBody>
        </Table>

        {!isLoading && tableData.length === 0 && (
          <div className="w-full flex justify-center">
            {t("crawler_stats.no_stats")}
          </div>
        )}
      </div>
    </Layout>
  );
};
