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

  const numSelectedRows = table.getFilteredSelectedRowModel().rows.length;
  const canDelete = numSelectedRows > 0;

  function handleDeleteSelected() {
    if (!canDelete) {
      const selectedIds = table
        .getSelectedRowModel()
        .rows.map((row) => row.original);

      // Implement actual deletion, when Endpoint ready:
      //const newData = data.filter((row) => !selectedIds.includes(row));
      // Update state (if you store data in parent)
      console.log("Delete these IDs:", selectedIds);
    } else return;
  }

  const users = [
    { clerk_id: 1234, email: "leo@tum.de" },
    { clerk_id: 2345, email: "rafael@tum.de" },
    { clerk_id: 3456, email: "jonathan@tum.de" },
    { clerk_id: 3456, email: "leo@bmw.com" },
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
            onClick={() => handleDeleteSelected()}
          >
            <Trash2 className="h-4 w-4" />
            {t("Delete")} ({numSelectedRows})
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
      </Table>

      <ScrollArea className="h-[200px]">
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
                  {t("admin.no_results")}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </ScrollArea>
    </>
  );
}
