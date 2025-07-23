import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from "~/components/ui/table";
import * as React from "react";

import {
  type ColumnDef,
  type ColumnFiltersState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  type SortingState,
  useReactTable,
  type VisibilityState,
  type RowData,
} from "@tanstack/react-table";
import { ArrowDownUp, Search, SortAsc, SortDesc } from "lucide-react";
import { Input } from "~/components/ui/input";
import { Switch } from "~/components/ui/switch";
import type { Subscription } from "../../../../types/model";
import { useTranslation } from "react-i18next";
import type { TFunction } from "i18next";
import { Skeleton } from "~/components/ui/skeleton";
import { ScrollArea } from "~/components/ui/scroll-area";
import { cn } from "~/lib/utils";

export interface MailingTableProps {
  name: string;
  allSubscriptions: Subscription[];
  setSubscriptions: (subscriptions: Subscription[]) => void;
  isLoading?: boolean;
}

type DataRow = {
  data: Subscription;
  active: boolean;
};

declare module "@tanstack/react-table" {
  interface TableMeta<TData extends RowData> {
    updateData: (
      rowIndex: number,
      columnId: keyof TData,
      value: unknown,
    ) => void;
  }
}

const getColumns = (
  name: string,
  t: TFunction,
  addSubscription: (s: Subscription) => void,
  removeSubscription: (s: Subscription) => void,
): ColumnDef<DataRow>[] => [
  {
    id: "data",
    accessorFn: (row) => row.data.name,
    cell: ({ row }) => <div>{row.getValue("data")}</div>,
    header: t("subscriptions.source"),
  },
  {
    accessorKey: "active",
    header: t("subscriptions.active"),
    cell: ({ row, table }) => (
      <Switch
        checked={row.getValue("active")}
        onCheckedChange={(value) => {
          table.options.meta?.updateData(row.index, "active", !!value);
          if (value) {
            addSubscription(row.original.data);
          } else {
            removeSubscription(row.original.data);
          }
        }}
        aria-label="Toggle active state"
      />
    ),
    enableSorting: true,
    sortingFn: "basic",
  },
];

export function DataTableSubscriptions({
  name,
  allSubscriptions,
  setSubscriptions,
  isLoading = false,
}: MailingTableProps) {
  const [sorting, setSorting] = React.useState<SortingState>([
    { id: "active", desc: true },
  ]);
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    [],
  );
  const [columnVisibility, setColumnVisibility] =
    React.useState<VisibilityState>({});
  const [rowSelection, setRowSelection] = React.useState({});

  const [internalData, setInternalData] = React.useState<DataRow[]>(() =>
    allSubscriptions.map((item) => ({
      data: item,
      active: item.is_subscribed,
    })),
  );

  const addSubscription = (sub: Subscription) => {
    const updatedSub = { ...sub, is_subscribed: true };
    const updatedSubscriptions = allSubscriptions.map((s) =>
      s.id === sub.id ? updatedSub : s,
    );
    setSubscriptions(updatedSubscriptions);
  };

  const removeSubscription = (sub: Subscription) => {
    const updatedSub = { ...sub, is_subscribed: false };
    const updatedSubscriptions = allSubscriptions.map((s) =>
      s.id === sub.id ? updatedSub : s,
    );
    setSubscriptions(updatedSubscriptions);
  };

  React.useEffect(() => {
    setInternalData((currentInternalData) =>
      allSubscriptions.map((item) => {
        const existingRow = currentInternalData.find(
          (d) => d.data.id === item.id,
        );

        if (existingRow && existingRow.data === item) {
          return existingRow;
        }

        return {
          data: item,
          active: existingRow ? existingRow.active : item.is_subscribed,
        };
      }),
    );
  }, [allSubscriptions]);

  const { t } = useTranslation();

  const columns = React.useMemo(
    () => getColumns(name, t, addSubscription, removeSubscription),
    [name, addSubscription, removeSubscription],
  );

  const table = useReactTable({
    data: internalData,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection,
    },
    meta: {
      updateData: (rowIndex, columnId, value) => {
        setInternalData((old) =>
          old.map((row, index) => {
            if (index === rowIndex) {
              return {
                ...old[index]!,
                [columnId as keyof DataRow]: value,
              };
            }
            return row;
          }),
        );
      },
    },
  });

  if (isLoading) {
    return (
      <div className="w-full h-full">
        <div className="flex items-center py-4 justify-between">
          <Skeleton className="h-10 w-64 rounded-md" />
        </div>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>
                <Skeleton className="h-5 w-32" />
              </TableHead>
              <TableHead>
                <Skeleton className="h-5 w-24" />
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {[...Array(5)].map((_, idx) => (
              <TableRow key={idx}>
                <TableCell>
                  <Skeleton className="h-4 w-48" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-6 w-10 rounded-full" />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    );
  }

  return (
    <div className="w-full h-full pb-28 overflow-hidden">
      <div className="relative flex items-center py-4 justify-between">
        <Input
          placeholder={
            "Filter " +
            (name === "Source" ? name.toLowerCase() + "s..." : name + "n...")
          }
          value={(table.getColumn("data")?.getFilterValue() as string) ?? ""}
          onChange={(event) =>
            table.getColumn("data")?.setFilterValue(event.target.value)
          }
        />
        <Search size={20} className="absolute right-3 text-muted-foreground" />
      </div>
      <Table>
        <TableHeader className="bg-blue-100">
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id} className="grid grid-cols-7">
              {headerGroup.headers.map((header) => {
                const canSort = header.column.getCanSort();
                const sortingState = header.column.getIsSorted();
                const sortingIndex = header.column.getSortIndex();
                return (
                  <TableHead
                    key={header.id}
                    onClick={
                      canSort
                        ? header.column.getToggleSortingHandler()
                        : undefined
                    }
                    className={cn(
                      // eslint-disable-next-line @typescript-eslint/no-explicit-any
                      ((header.column.columnDef.meta as any)?.className ?? "") +
                        (header.column.getCanSort()
                          ? " cursor-pointer select-none"
                          : ""),
                      "flex items-center",
                      header.id === "data" ? "col-span-6" : "col-span-1",
                    )}
                  >
                    {header.isPlaceholder ? null : (
                      <span className="me-1">
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext(),
                        )}
                      </span>
                    )}
                    {sortingIndex && sortingIndex >= 0 ? (
                      <span>{sortingIndex + 1}</span>
                    ) : undefined}
                    {canSort ? (
                      sortingState === "asc" ? (
                        <SortAsc className="inline size-4" />
                      ) : sortingState === "desc" ? (
                        <SortDesc className="inline size-4" />
                      ) : (
                        <ArrowDownUp className="inline size-4 opacity-50" />
                      )
                    ) : null}
                  </TableHead>
                );
              })}
            </TableRow>
          ))}
        </TableHeader>
      </Table>
      <ScrollArea className="h-full">
        <Table>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  {t("subscriptions.no_results")}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </ScrollArea>
    </div>
  );
}
