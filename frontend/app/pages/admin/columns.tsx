import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import type { ColumnDef } from "@tanstack/react-table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "~/components/ui/dropdown-menu";
import { MoreHorizontal, SquarePen, Trash, Trash2 } from "lucide-react";
import { Button } from "~/components/ui/button";
import { Checkbox } from "~/components/ui/checkbox";
import { useTranslation } from "react-i18next";
import type { Organization, Subscription } from "../../../types/model";
import type { TableUser } from "../admin/dialogs/organization-dialog";

export function getOrgaColumns(
  handleEdit: (org: Organization) => void,
  setDeleteTarget: React.Dispatch<
    React.SetStateAction<{
      type: "organization" | "subscription";
      data: Organization | Subscription;
    } | null>
  >,
  setOpenDeleteDialog: React.Dispatch<React.SetStateAction<boolean>>,
): ColumnDef<Organization>[] {
  const { t } = useTranslation();
  return [
    {
      accessorKey: "name",
      header: "Name",
    },
    {
      id: "actions",
      header: "Options",
      cell: ({ row }) => {
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <span className="sr-only">Open menu</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => handleEdit(row.original)}>
                <SquarePen className="text-primary" />
                {t("Edit")}
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => {
                  setDeleteTarget({
                    type: "organization",
                    data: row.original,
                  });
                  setOpenDeleteDialog(true);
                }}
                className="text-red-500 focus:text-red-500"
              >
                <Trash2 className="text-red-500" />
                {t("Delete")}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ];
}

export function getSubsColumns(
  handleEdit: (sub: Subscription) => void,
  setDeleteTarget: React.Dispatch<
    React.SetStateAction<{
      type: "organization" | "subscription";
      data: Organization | Subscription;
    } | null>
  >,
  setOpenDeleteDialog: React.Dispatch<React.SetStateAction<boolean>>,
): ColumnDef<Subscription>[] {
  const { t } = useTranslation();
  return [
    {
      accessorKey: "name",
      header: "Name",
    },
    {
      id: "actions",
      header: "Options",
      cell: ({ row }) => {
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <span className="sr-only">Open menu</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => handleEdit(row.original)}>
                <SquarePen className="text-primary" />
                {t("Edit")}
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => {
                  setDeleteTarget({ type: "subscription", data: row.original });
                  setOpenDeleteDialog(true);
                }}
                className="text-red-500 focus:text-red-500"
              >
                <Trash2 className="text-red-500" />
                {t("Delete")}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ];
}

export function getUserColumns(
  onRoleChange: (index: number, role: "admin" | "user") => void,
  onDelete: (index: number) => void,
): ColumnDef<TableUser>[] {
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
      accessorKey: "username",
      header: t("general.Username"),
    },
    {
      accessorKey: "role",
      header: t("organization-dialog.role"),
      cell: ({ row }) => {
        const role = row.getValue("role") as "admin" | "user";
        const index = row.index;

        return (
          <Select
            value={role}
            onValueChange={(newRole) => {
              onRoleChange(index, newRole as "admin" | "user");
            }}
          >
            <SelectTrigger className="w-[120px]">
              <SelectValue placeholder="Select role" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="admin">
                {t("organization-dialog.admin")}
              </SelectItem>
              <SelectItem value="user">
                {t("organization-dialog.user")}
              </SelectItem>
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
