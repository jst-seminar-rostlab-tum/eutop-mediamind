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
import { Checkbox } from "~/components/ui/checkbox";
import { Button } from "~/components/ui/button";
import { ArrowUpDown, Plus, Trash, Trash2 } from "lucide-react";

import { Input } from "~/components/ui/input";
import { useTranslation } from "react-i18next";
import { ScrollArea } from "~/components/ui/scroll-area";
import { cn } from "~/lib/utils";

export interface MailingTableProps {
  name: string;
  dataArray: string[];
  setDataArray: (array: string[]) => void;
}

type DataRow = {
  data: string;
};

const getColumns = (
  name: string,
  setDataArray: (data: string[]) => void,
  dataArray: string[],
): ColumnDef<DataRow>[] => [
  {
    id: "select",
    header: ({ table }) => (
      <Checkbox
        checked={
          table.getIsAllPageRowsSelected() ||
          (table.getIsSomePageRowsSelected() && "indeterminate")
        }
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
        aria-label="Select all"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value) => row.toggleSelected(!!value)}
        aria-label="Select row"
      />
    ),
    enableSorting: false,
    enableHiding: false,
  },
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
    id: "actions",
    enableHiding: false,
    cell: ({ row }) => {
      return (
        <Button
          variant={"ghost"}
          onClick={() =>
            setDataArray(
              dataArray.filter((email) => email !== row.original.data),
            )
          }
        >
          <Trash className="text-destructive" />
        </Button>
      );
    },
  },
];

export function DataTableMailing({
  name,
  dataArray,
  setDataArray,
}: MailingTableProps) {
  const [sorting, setSorting] = React.useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    [],
  );
  const [columnVisibility, setColumnVisibility] =
    React.useState<VisibilityState>({});
  const [rowSelection, setRowSelection] = React.useState({});

  const columns = React.useMemo(
    () => getColumns(name, setDataArray, dataArray),
    [name, setDataArray, dataArray],
  );
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
    getRowId: (row) => row.data,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection,
    },
  });

  const numSelectedRows = table.getFilteredSelectedRowModel().rows.length;
  const canDelete = numSelectedRows > 0;

  const handleDeleteSelected = () => {
    if (!canDelete) return;
    const selectedMails = table
      .getSelectedRowModel()
      .rows.map((row) => row.original.data);
    setDataArray(dataArray.filter((email) => !selectedMails.includes(email)));
  };

  const [email, setEmail] = React.useState("");

  const handleAddEmail = () => {
    if (!email) return; // prevent empty
    if (dataArray.includes(email)) return; // prevent duplicates

    const updatedArray = [...dataArray, email];
    setDataArray(updatedArray);
    setEmail(""); // clear input
  };

  const { t } = useTranslation();

  return (
    <div className="w-full">
      <div className="flex items-center py-4 justify-between">
        <Input
          placeholder={`Filter ${name.toLowerCase()}s...`}
          value={(table.getColumn("data")?.getFilterValue() as string) ?? ""}
          onChange={(event) =>
            table.getColumn("data")?.setFilterValue(event.target.value)
          }
          className="max-w-50"
        />
        <div className="flex items-center space-x-2">
          <div className={"flex "}>
            <Input
              placeholder="Email"
              name="email"
              className={"rounded-r-none"}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <Button
              className={"rounded-l-none"}
              variant={"secondary"}
              onClick={() => handleAddEmail()}
            >
              <Plus className={"h-4 w-4"} />
              {t("Add")}
            </Button>
          </div>

          <Button
            variant="destructive"
            onClick={handleDeleteSelected}
            disabled={!canDelete}
            className={!canDelete ? "cursor-not-allowed opacity-50" : ""}
          >
            <Trash2 className="h-4 w-4" />
            {t("Delete")} ({numSelectedRows})
          </Button>
        </div>
      </div>
      <Table>
        <TableHeader className="bg-blue-100">
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id} className="grid grid-cols-8">
              {headerGroup.headers.map((header, idx) => {
                return (
                  <TableHead
                    key={header.id}
                    className={cn(
                      "flex items-center",
                      idx === 0 || idx === 2
                        ? "col-span-1 justify-center"
                        : "col-span-6 ",
                    )}
                  >
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
      </Table>
      <ScrollArea className="h-full">
        <Table>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  className="grid grid-cols-8"
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                >
                  {row.getVisibleCells().map((cell, idx) => (
                    <TableCell
                      key={cell.id}
                      className={cn(
                        "flex items-center",
                        idx === 0 || idx === 2
                          ? "col-span-1 justify-center"
                          : "col-span-6",
                      )}
                    >
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
                  {t("data-table-mailing.no_results")}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </ScrollArea>
      <div className="flex items-center justify-end space-x-2 py-4">
        <div className="flex-1 text-sm text-muted-foreground">
          {numSelectedRows} {t("data-table-mailing.of")}{" "}
          {table.getFilteredRowModel().rows.length}{" "}
          {t("data-table-mailing.rows_selected")}
        </div>
      </div>
    </div>
  );
}
