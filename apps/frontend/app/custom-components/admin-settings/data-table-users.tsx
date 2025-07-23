import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  useReactTable,
  type ColumnDef,
  type ColumnFiltersState,
  type Row,
} from "@tanstack/react-table";
import { Check, ChevronsUpDown, Plus, Trash2 } from "lucide-react";
import React from "react";
import { useTranslation } from "react-i18next";
import type { MediamindUser } from "types/model";
import { Button } from "~/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "~/components/ui/command";
import { Input } from "~/components/ui/input";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "~/components/ui/popover";
import { ScrollArea } from "~/components/ui/scroll-area";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "~/components/ui/table";
import { cn } from "~/lib/utils";

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
  onAdd: (email: string) => void;
  users: MediamindUser[];
  onBunchDelete: (selectedRows: Row<TData>[]) => void;
}

export function DataTableUsers<TData, TValue>({
  columns,
  data,
  onAdd,
  users,
  onBunchDelete,
}: DataTableProps<TData, TValue>) {
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    [],
  );
  const [selectedEmail, setSelectedEmail] = React.useState<string>("");

  const [rowSelection, setRowSelection] = React.useState({});

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    onColumnFiltersChange: setColumnFilters,
    getFilteredRowModel: getFilteredRowModel(),
    enableRowSelection: true,
    onRowSelectionChange: setRowSelection,
    state: {
      columnFilters,
      rowSelection,
    },
  });

  const [open, setOpen] = React.useState(false);

  const canDelete = table.getFilteredSelectedRowModel().rows.length > 0;

  const { t } = useTranslation();

  return (
    <>
      <div className="flex justify-between gap-4 mb-4">
        <Input
          placeholder={"Filter " + t("general.Users")}
          value={(table.getColumn("email")?.getFilterValue() as string) ?? ""}
          onChange={(event) => {
            table.getColumn("email")?.setFilterValue(event.target.value);
          }}
          className="max-w-1/2"
        />
        <div className="flex gap-4 justify-items-end">
          <div className="flex">
            <Popover open={open} onOpenChange={setOpen}>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  role="combobox"
                  aria-expanded={open}
                  className={cn(
                    "rounded-r-none min-w-[150px] justify-between",
                    !selectedEmail && "text-muted-foreground",
                  )}
                >
                  {selectedEmail
                    ? users.find((user) => user.email === selectedEmail)?.email
                    : t("admin.add_user")}
                  <ChevronsUpDown className="opacity-50" />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-fit p-0">
                <Command>
                  <CommandInput
                    placeholder={t("admin.search_user")}
                    className="h-9"
                  />
                  <CommandList>
                    <CommandEmpty>{t("admin.no_user")}</CommandEmpty>
                    <CommandGroup>
                      {users.map((user) => (
                        <CommandItem
                          key={user.id}
                          value={user.email}
                          onSelect={(currentValue) => {
                            setSelectedEmail(currentValue);
                            setOpen(false);
                          }}
                        >
                          {user.email}
                          <Check
                            className={cn(
                              "ml-auto",
                              table
                                .getRowModel()
                                .rows.some(
                                  (row) => row.getValue("email") === user.email,
                                )
                                ? "opacity-100"
                                : "opacity-0",
                            )}
                          />
                        </CommandItem>
                      ))}
                    </CommandGroup>
                  </CommandList>
                </Command>
              </PopoverContent>
            </Popover>
            <Button
              className={"rounded-l-none"}
              variant={"secondary"}
              onClick={(e) => {
                e.preventDefault();
                onAdd(selectedEmail);
                setSelectedEmail("");
              }}
            >
              <Plus className={"h-4 w-4"} />
              {t("Add")}
            </Button>
          </div>

          <Button
            disabled={!canDelete}
            className={!canDelete ? "cursor-not-allowed opacity-50" : ""}
            variant="destructive"
            onClick={(e) => {
              e.preventDefault();
              onBunchDelete(table.getSelectedRowModel().rows);
              setRowSelection({});
            }}
          >
            <Trash2 className="h-4 w-4" />
            {t("Delete")} ({table.getFilteredSelectedRowModel().rows.length})
          </Button>
        </div>
      </div>
      <Table>
        <TableHeader className="bg-blue-100">
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id} className="grid grid-cols-20">
              {headerGroup.headers.map((header) => {
                return (
                  <TableHead
                    key={header.id}
                    className={cn(
                      "flex items-center",
                      header.index === 0 || header.index === 4
                        ? "col-span-1 justify-center"
                        : header.index === 3
                          ? "col-span-4"
                          : "col-span-7",
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

      <ScrollArea className="h-[400px]">
        <Table>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                  className="grid grid-cols-20"
                >
                  {row.getVisibleCells().map((cell, idx) => (
                    <TableCell
                      key={cell.id}
                      className={cn(
                        "flex items-center",
                        idx === 0 || idx === 4
                          ? "col-span-1 justify-center"
                          : idx === 3
                            ? "col-span-4"
                            : "col-span-7",
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
                  {t("organization-dialog.no_results")}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </ScrollArea>
    </>
  );
}
