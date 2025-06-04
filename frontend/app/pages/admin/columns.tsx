import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import {
  AlertDialog,
  AlertDialogTrigger,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogFooter,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogCancel,
  AlertDialogAction,
} from "~/components/ui/alert-dialog";
import type { Organization, Subscription, User } from "./types";
import type { ColumnDef } from "@tanstack/react-table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "~/components/ui/dropdown-menu";
import { MoreHorizontal, Trash } from "lucide-react";
import { Button } from "~/components/ui/button";

export function getOrgaColumns(
  handleEdit: (name: string) => void,
  handleDelete: (name: string) => void,
): ColumnDef<Organization>[] {
  return [
    {
      accessorKey: "name",
      header: "Organization Name",
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
                Edit Organization
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => handleDelete(orgName)}
                className="text-red-500"
              >
                Delete Organization
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
  onDelete: (index: number) => void,
): ColumnDef<Subscription>[] {
  return [
    { accessorKey: "name", header: "Subscriptions" },
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
                Edit Subscription
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => onDelete(index)}
                className="text-red-500"
              >
                Delete Subscription
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
  return [
    {
      accessorKey: "name",
      header: "User",
    },
    {
      accessorKey: "role",
      header: "Role",
      cell: ({ row }) => {
        const role = row.getValue("role") as "admin" | "user";
        const index = row.index;

        return (
          <Select
            value={role}
            onValueChange={(newRole) =>
              onRoleChange(index, newRole as "admin" | "user")
            }
          >
            <SelectTrigger className="w-[120px]">
              <SelectValue placeholder="Select role" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="admin">admin</SelectItem>
              <SelectItem value="user">user</SelectItem>
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
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant={"ghost"}>
                <Trash className="text-red-500" />
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                <AlertDialogDescription>
                  This will permanently remove the user from this organization.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={() => onDelete(index)}>
                  Delete
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        );
      },
    },
  ];
}
