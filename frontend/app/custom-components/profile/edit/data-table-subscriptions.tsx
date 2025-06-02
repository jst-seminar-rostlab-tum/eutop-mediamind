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
import { ScrollArea } from "~/components/ui/scroll-area";
import { Switch } from "~/components/ui/switch";

export interface MailingTableProps {
  name: string;
  dataArray: string[];
}

type DataRow = {
  data: string;
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

export const getColumns = (name: string): ColumnDef<DataRow>[] => [
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
    cell: ({ row }) => <div className="lowercase">{row.getValue("data")}</div>,
  },
  {
    accessorKey: "active",
    header: "Active",
    cell: ({ row, table }) => (
      <Switch
        checked={row.getValue("active")}
        onCheckedChange={(value) => {
          table.options.meta?.updateData(row.index, "active", !!value);
        }}
        aria-label="Toggle active state"
      />
    ),
    enableSorting: true,
  },
];

export function DataTableSubsciptions({ name, dataArray }: MailingTableProps) {
  const [sorting, setSorting] = React.useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    [],
  );
  const [columnVisibility, setColumnVisibility] =
    React.useState<VisibilityState>({});
  const [rowSelection, setRowSelection] = React.useState({});

  const [internalData, setInternalData] = React.useState<DataRow[]>(() =>
    dataArray.map((item) => ({
      data: item,
      active: true,
    })),
  );

  React.useEffect(() => {
    setInternalData((currentInternalData) =>
      dataArray.map((item) => {
        const existingRow = currentInternalData.find((d) => d.data === item);
        return {
          data: item,
          active: existingRow ? existingRow.active : true,
        };
      }),
    );
  }, [dataArray]);

  const columns = React.useMemo(() => getColumns(name), [name]);

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
      <ScrollArea className={"h-[400px] rounded-md border"}>
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
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </ScrollArea>
      <div className="flex items-center justify-end space-x-2 py-4">
        <div className="flex-1 text-sm text-muted-foreground">
          {table.getFilteredSelectedRowModel().rows.length} of{" "}
          {table.getFilteredRowModel().rows.length} row(s) selected.
        </div>
      </div>
    </div>
  );
}
