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
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogFooter,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogCancel,
  AlertDialogAction,
} from "~/components/ui/alert-dialog";

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
  unsavedEdits: boolean;
  setUnsavedEdits: (val: boolean) => void;
  initialOrgaName: string;
  showAlert: boolean;
  setShowAlert: (val: boolean) => void;
  showOrgaNameAlert: boolean;
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
  unsavedEdits,
  setUnsavedEdits,
  initialOrgaName,
  showAlert,
  setShowAlert,
  showOrgaNameAlert,
}: Props) {
  const [showLeaveConfirm, setShowLeaveConfirm] = React.useState(false);

  const handleRoleChange = (index: number, newRole: "admin" | "user") => {
    setUsers(users.map((u, i) => (i === index ? { ...u, role: newRole } : u)));
    setUnsavedEdits(true);
  };

  const handleUserDelete = (index: number) => {
    setUsers(users.filter((_, i) => i !== index));
    setUnsavedEdits(true);
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
    setUnsavedEdits(true);
  };

  return (
    <>
      <Dialog
        open={open}
        onOpenChange={(isOpen) => {
          const nameChanged = initialOrgaName !== name;

          if (!isOpen && (unsavedEdits || nameChanged)) {
            setShowLeaveConfirm(true); // show AlertDialog instead
          } else {
            onOpenChange(isOpen); // normal open/close
          }
        }}
      >
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
          {showOrgaNameAlert && (
            <Alert className="mt-2" variant="destructive">
              <AlertCircleIcon />
              <AlertTitle>Organization Name is Empty</AlertTitle>
              <AlertDescription>
                Please insert a valid Organization Name
              </AlertDescription>
            </Alert>
          )}
          <div className="grid grid-cols-4 items-center gap-4">
            <Label className="text-right">Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => {
                onNameChange(e.target.value);
              }}
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

      <AlertDialog open={showLeaveConfirm} onOpenChange={setShowLeaveConfirm}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              You have unsaved changes right now
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-white shadow-xs hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60"
              onClick={() => {
                setShowLeaveConfirm(false);
                onOpenChange(false); // close the main dialog
              }}
            >
              Leave
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
