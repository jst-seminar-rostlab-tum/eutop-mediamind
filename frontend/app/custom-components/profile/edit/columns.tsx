import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import type { ColumnDef } from "@tanstack/react-table";

import { Trash } from "lucide-react";
import { Button } from "~/components/ui/button";
import { Checkbox } from "~/components/ui/checkbox";
import { useTranslation } from "react-i18next";
import type { UserWithRole } from "../edit/general";

export function getUserColumns(
  onRoleChange: (index: number, role: "read" | "edit") => void,
  onDelete: (index: number) => void,
): ColumnDef<UserWithRole>[] {
  const { t } = useTranslation();
  return [
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
      accessorKey: "email",
      header: t("general.Email"),
      filterFn: (row, _, filterValue: string) => {
        const email = row.original.email?.toLowerCase() || "";
        const username = row.original.username?.toLowerCase() || "";
        const value = filterValue.toLowerCase();
        return email.includes(value) || username.includes(value);
      },
    },
    {
      accessorKey: "Username",
      header: t("general.Username"),
    },
    {
      accessorKey: "rights",
      header: t("general.Rights"),
      cell: ({ row }) => {
        const rights = row.getValue("rights") as "read" | "edit";
        const index = row.index;

        return (
          <Select
            value={rights}
            onValueChange={(newRights) => {
              onRoleChange(index, newRights as "read" | "edit");
            }}
          >
            <SelectTrigger className="w-[120px]">
              <SelectValue placeholder="Select role" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="read">{t("general.read")}</SelectItem>
              <SelectItem value="edit">{t("general.edit")}</SelectItem>
            </SelectContent>
          </Select>
        );
      },
    },
    {
      id: "actions",
      cell: ({ row }) => {
        const index = row.index;
        return (
          <Button variant={"ghost"} onClick={() => onDelete(index)}>
            <Trash className="text-red-500" />
          </Button>
        );
      },
    },
  ];
}
