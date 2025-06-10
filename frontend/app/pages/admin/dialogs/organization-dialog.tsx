import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "~/components/ui/dialog";
import { Label } from "@radix-ui/react-dropdown-menu";
import { Input } from "~/components/ui/input";
import { Button } from "~/components/ui/button";
import { DataTable } from "~/custom-components/data-table";
import { getUserColumns } from "../columns";
import type { User } from "../types";
import { Alert, AlertDescription, AlertTitle } from "~/components/ui/alert";
import React from "react";
import { AlertCircleIcon } from "lucide-react";

type Props = {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  isEdit: boolean;
  name: string;
  onNameChange: (value: string) => void;
  users: User[];
  setUsers: (users: User[]) => void;
  searchInput: string;
  setSearchInput: (value: string) => void;
  onSave: () => void;
};

export function OrganizationDialog({
  open,
  onOpenChange,
  isEdit,
  name,
  onNameChange,
  users,
  setUsers,
  searchInput,
  setSearchInput,
  onSave,
}: Props) {
  const [showAlert, setShowAlert] = React.useState(false);

  const handleRoleChange = (index: number, newRole: "admin" | "user") => {
    setUsers(users.map((u, i) => (i === index ? { ...u, role: newRole } : u)));
  };

  const handleUserDelete = (index: number) => {
    setUsers(users.filter((_, i) => i !== index));
  };

  const handleAddNewUser = () => {
    const email = searchInput.trim().toLowerCase();
    // check if email matches "something@something.something" format and does not already exist
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (
      !emailRegex.test(email) ||
      users.some((u) => u.name.toLowerCase() === email)
    ) {
      setShowAlert(true);
      return;
    }
    // add user
    setShowAlert(false);
    setUsers([...users, { name: email, role: "user" }]);
    setSearchInput("");
  };

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>
              {isEdit ? "Edit Organization" : "Add Organization"}
            </DialogTitle>
            <DialogDescription>
              {isEdit
                ? "Edit your organization here. Click save when you're done."
                : "Enter the name of the organization you want to add. Click save when you're done."}
            </DialogDescription>
          </DialogHeader>

          <div className="grid grid-cols-4 items-center gap-4">
            <Label className="text-right">Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => onNameChange(e.target.value)}
              placeholder="New Organization"
              className="col-span-3"
            />
          </div>
          {showAlert && (
            <Alert className="mt-2" variant="destructive">
              <AlertCircleIcon />
              <AlertTitle>Invalid Email</AlertTitle>
              <AlertDescription>
                Please insert a valid and unique email address.
              </AlertDescription>
            </Alert>
          )}
          <div className="mt-2">
            <DataTable
              columns={getUserColumns(handleRoleChange, handleUserDelete)}
              data={users}
              onSearchChange={setSearchInput}
              onAdd={handleAddNewUser}
            />
          </div>

          <DialogFooter>
            <Button type="submit" onClick={onSave}>
              Save changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
