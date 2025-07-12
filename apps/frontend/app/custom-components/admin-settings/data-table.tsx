import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  type ColumnFiltersState,
  getFilteredRowModel,
  type ColumnDef,
  type SortingState,
  getSortedRowModel,
} from "@tanstack/react-table";
import { ArrowDownUp, Plus, SortAsc, SortDesc } from "lucide-react";
import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "~/components/ui/table";

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
  onAdd?: () => void;
  onSearchChange?: (value: string) => void;
  searchField?: keyof TData | string;
}

export function DataTable<TData, TValue>({
  columns,
  data,
  onAdd,
  onSearchChange,
  searchField = "name",
}: DataTableProps<TData, TValue>) {
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    [],
  );
  const [sorting, setSorting] = useState<SortingState>([]);

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    onColumnFiltersChange: setColumnFilters,
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    state: {
      columnFilters,
      sorting,
    },
    defaultColumn: {
      enableSorting: false,
    },
  });

  const { t } = useTranslation();

  return (
    <>
      <div className="flex items-center py-4">
        <Input
          placeholder={t("search")}
          value={
            (table
              .getColumn(searchField as string)
              ?.getFilterValue() as string) ?? ""
          }
          onChange={(event) => {
            const value = event.target.value;
            table.getColumn(searchField as string)?.setFilterValue(value);
            onSearchChange?.(value); // send value to parent
          }}
        />
        {onAdd && (
          <Button variant={"outline"} className="ml-4" onClick={onAdd}>
            {t("Add")}
            <Plus />
          </Button>
        )}
      </div>
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
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
                    className={
                      // eslint-disable-next-line @typescript-eslint/no-explicit-any
                      ((header.column.columnDef.meta as any)?.className ?? "") +
                      (header.column.getCanSort()
                        ? " cursor-pointer select-none"
                        : "")
                    }
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
        <TableBody>
          {table.getRowModel().rows?.length ? (
            table.getRowModel().rows.map((row) => (
              <TableRow
                key={row.id}
                data-state={row.getIsSelected() && "selected"}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell
                    key={cell.id}
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                    className={(cell.column.columnDef.meta as any)?.className}
                  >
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
    </>
  );
}
