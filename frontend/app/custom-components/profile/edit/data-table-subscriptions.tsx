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
import { Button } from "~/components/ui/button";
import { ArrowUpDown } from "lucide-react";
import { Input } from "~/components/ui/input";
import { Switch } from "~/components/ui/switch";
import type { Subscription } from "../../../../types/model";
import { useTranslation } from "react-i18next";
import type { TFunction } from "i18next";

export interface MailingTableProps {
  name: string;
  allSubscriptions: Subscription[];
  setSubscriptions: (subscriptions: Subscription[]) => void;
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
    accessorKey: "data",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          {name}
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      );
    },
    cell: ({ row }) => (
      <div className="lowercase">{row.getValue<Subscription>("data").name}</div>
    ),
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
            addSubscription(row.getValue("data"));
          } else {
            removeSubscription(row.getValue("data"));
          }
        }}
        aria-label="Toggle active state"
      />
    ),
    enableSorting: true,
  },
];

export function DataTableSubscriptions({
  name,
  allSubscriptions,
  setSubscriptions,
}: MailingTableProps) {
  const [sorting, setSorting] = React.useState<SortingState>([]);
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

  return (
    <div className="w-full">
      <div className="flex items-center py-4 justify-between">
        <Input
          placeholder={
            "Filter " +
            (name === "Source" ? name.toLowerCase() + "s..." : name + "n...")
          }
          value={(table.getColumn("data")?.getFilterValue() as string) ?? ""}
          onChange={(event) =>
            table.getColumn("data")?.setFilterValue(event.target.value)
          }
          className="max-w-sm"
        />
      </div>
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
              {headerGroup.headers.map((header) => {
                return (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext(),
                        )}
                  </TableHead>
                );
              })}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows?.length ? (
            table.getRowModel().rows.map((row) => (
              <TableRow
                key={row.id}
                data-state={row.getIsSelected() && "selected"}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={columns.length} className="h-24 text-center">
                {t("data-table-subscriptions.no_results")}
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
