import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import type { Organization, Subscription, User, DeleteTarget } from "./types";
import type { ColumnDef } from "@tanstack/react-table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "~/components/ui/dropdown-menu";
import { MoreHorizontal, Trash } from "lucide-react";
import { Button } from "~/components/ui/button";
import { Checkbox } from "~/components/ui/checkbox";
import { useTranslation } from "react-i18next";

export function getOrgaColumns(
  handleEdit: (name: string) => void,
  setDeleteTarget: (target: DeleteTarget) => void,
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
      cell: ({ row }) => {
        const orgName = row.getValue("name") as string;
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <span className="sr-only">Open menu</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => handleEdit(orgName)}>
                {t("Edit")}
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => {
                  setDeleteTarget({
                    type: "organization",
                    identifier: orgName,
                  });
                  setOpenDeleteDialog(true);
                }}
                className="text-destructive"
              >
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
  onEdit: (index: number) => void,
  setDeleteTarget: (target: DeleteTarget) => void,
  setOpenDeleteDialog: React.Dispatch<React.SetStateAction<boolean>>,
): ColumnDef<Subscription>[] {
  const { t } = useTranslation();
  return [
    { accessorKey: "name", header: "Name" },
    { accessorKey: "url", header: "URL" },
    {
      id: "actions",
      cell: ({ row }) => {
        const index = row.index;
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <span className="sr-only">Open menu</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onEdit(index)}>
                {t("Edit")}
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => {
                  setDeleteTarget({ type: "subscription", identifier: index });
                  setOpenDeleteDialog(true);
                }}
                className="text-destructive"
              >
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
): ColumnDef<User>[] {
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
      accessorKey: "name",
      header: "User",
    },
    {
      accessorKey: "role",
      header: t("admin.role"),
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
              <SelectItem value="admin">{t("admin.admin")}</SelectItem>
              <SelectItem value="user">{t("admin.user")}</SelectItem>
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
            <Trash className="text-destructive" />
          </Button>
        );
      },
    },
  ];
}
