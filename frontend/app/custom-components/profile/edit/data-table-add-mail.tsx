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
} from "@tanstack/react-table";
import { Button } from "~/components/ui/button";
import { ArrowUpDown, Plus, Trash } from "lucide-react";

import { Input } from "~/components/ui/input";
import { ScrollArea } from "~/components/ui/scroll-area";

export interface MailingTableProps {
  name: string;
  dataArray: string[];
}

type DataRow = {
  data: string;
};

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
    id: "delete",
    enableHiding: false,
    cell: () => {
      return <Trash className="h-4 w-4" />;
    },
  },
];

export function DataTableAddMail({ name, dataArray }: MailingTableProps) {
  const [sorting, setSorting] = React.useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    [],
  );
  const [columnVisibility, setColumnVisibility] =
    React.useState<VisibilityState>({});
  const [rowSelection, setRowSelection] = React.useState({});

  const columns = React.useMemo(() => getColumns(name), [name]);
  const data = React.useMemo(
    () =>
      dataArray.map((item) => ({
        data: item,
      })),
    [dataArray],
  );
  const table = useReactTable({
    data,
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
  });

  const numSelectedRows = table.getFilteredSelectedRowModel().rows.length;
  // const canDelete = numSelectedRows > 0;

  // const handleDeleteSelected = () => {
  //   if (!canDelete) return;
  //   // TODO: delete logic
  // };

  return (
    <div className="w-full">
      <div className="flex items-center py-4 justify-between gap-3">
        <Input
          placeholder={`Search`}
          value={(table.getColumn("data")?.getFilterValue() as string) ?? ""}
          onChange={(event) =>
            table.getColumn("data")?.setFilterValue(event.target.value)
          }
          className="max-w-sm"
        />

        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add
        </Button>
      </div>
      <ScrollArea className={"h-[400px]"}>
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
          {numSelectedRows} of {table.getFilteredRowModel().rows.length} row(s)
          selected.
        </div>
      </div>
    </div>
  );
}
