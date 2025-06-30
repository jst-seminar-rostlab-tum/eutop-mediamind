import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  useReactTable,
  type ColumnDef,
  type ColumnFiltersState,
} from "@tanstack/react-table";
import { Check, ChevronsUpDown, Plus, Trash2 } from "lucide-react";
import React from "react";
import { useTranslation } from "react-i18next";
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
}

export function DataTableUsers<TData, TValue>({
  columns,
  data,
  onAdd,
}: DataTableProps<TData, TValue>) {
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    [],
  );
  const [newEmail, setNewEmail] = React.useState("");

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    onColumnFiltersChange: setColumnFilters,
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      columnFilters,
    },
  });

  const handleDeleteSelected = () => {
    // you can call a prop like onDeleteMany if you implement one
    const selectedRows = table.getSelectedRowModel().rows;
    console.log(
      "To delete:",
      selectedRows.map((r) => r.original),
    );
  };

  const users = [
    { clerk_id: 1234, email: "leo@tum.de" },
    { clerk_id: 2345, email: "rafael@tum.de" },
    { clerk_id: 3456, email: "jonathan@tum.de" },
    { clerk_id: 3457, email: "leo@bmw.com" },
  ];

  const [open, setOpen] = React.useState(false);

  const { t } = useTranslation();

  return (
    <>
      <div className="flex justify-between gap-4">
        <Input
          placeholder={"Filter Emails..."}
          value={(table.getColumn("name")?.getFilterValue() as string) ?? ""}
          onChange={(event) => {
            table.getColumn("name")?.setFilterValue(event.target.value);
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
                    !newEmail && "text-muted-foreground",
                  )}
                >
                  {newEmail
                    ? users.find((user) => user.email === newEmail)?.email
                    : t("admin.add_user")}
                  <ChevronsUpDown className="opacity-50" />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-[250px] p-0">
                <Command>
                  <CommandInput placeholder="Search user..." className="h-9" />
                  <CommandList>
                    <CommandEmpty>{t("admin.no_user")}</CommandEmpty>
                    <CommandGroup>
                      {users.map((user) => (
                        <CommandItem
                          key={user.clerk_id}
                          value={user.email}
                          onSelect={(currentValue) => {
                            setNewEmail(currentValue);
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
                                  (row) => row.getValue("name") === user.email,
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
              onClick={() => {
                onAdd(newEmail);
                setNewEmail("");
              }}
            >
              <Plus className={"h-4 w-4"} />
              {t("Add")}
            </Button>
          </div>

          <Button
            className=""
            variant="destructive"
            onClick={handleDeleteSelected}
          >
            <Trash2 className="h-4 w-4" />
            {t("Delete")}
          </Button>
        </div>
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
                {t("admin.no_results")}
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </>
  );
}
