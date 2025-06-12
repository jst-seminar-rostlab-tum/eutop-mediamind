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
import type { Subscription } from "~/types/profile";

export interface MailingTableProps {
  name: string;
  allSubscriptions: Subscription[];
  selectedSubscriptions: Subscription[];
  setSubscriptions: (subs: Subscription[]) => void;
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
    header: "Active",
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

export function DataTableSubsciptions({
  name,
  allSubscriptions,
  selectedSubscriptions,
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
      active: selectedSubscriptions.map((s) => s.name).includes(item.name),
    })),
  );

  const addSubscription = (sub: Subscription) =>
    setSubscriptions([...selectedSubscriptions, sub]);

  const removeSubscription = (sub: Subscription) =>
    setSubscriptions(selectedSubscriptions.filter((s) => s.name !== sub.name));
  React.useEffect(() => {
    setInternalData((currentInternalData) =>
      allSubscriptions.map((item) => {
        const existingRow = currentInternalData.find(
          (d) => d.data.name === item.name,
        );
        return {
          data: item,
          active: existingRow
            ? existingRow.active
            : selectedSubscriptions.map((s) => s.name).includes(item.name),
        };
      }),
    );
  }, [allSubscriptions, selectedSubscriptions]);

  const columns = React.useMemo(
    () => getColumns(name, addSubscription, removeSubscription),
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
          placeholder={`Filter ${name.toLowerCase()}s...`}
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
                No results.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
