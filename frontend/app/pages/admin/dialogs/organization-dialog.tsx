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
import { getUserColumns } from "../columns";
import type { User } from "../types";
import { Alert, AlertDescription, AlertTitle } from "~/components/ui/alert";
import React from "react";
import { AlertCircleIcon, LogOut, OctagonAlert } from "lucide-react";
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
import { DataTableUsers } from "~/custom-components/admin-settings/data-table-users";
import { useTranslation } from "react-i18next";

type Props = {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  isEdit: boolean;
  name: string;
  onNameChange: (value: string) => void;
  users: User[];
  setUsers: (users: User[]) => void;
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

  const handleAddNewUser = (email: string) => {
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
    setUnsavedEdits(true);
  };

  const { t } = useTranslation();

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
        <DialogContent className="min-w-[700px]">
          <DialogHeader>
            <DialogTitle>
              {isEdit
                ? t("organization-dialog.edit_header")
                : t("organization-dialog.add_header")}
            </DialogTitle>
            <DialogDescription>
              {isEdit
                ? t("organization-dialog.edit_text")
                : t("organization-dialog.add_text")}
            </DialogDescription>
          </DialogHeader>
          {showOrgaNameAlert && (
            <Alert className="mt-2" variant="destructive">
              <AlertCircleIcon />
              <AlertTitle>
                {t("organization-dialog.name_error_header")}
              </AlertTitle>
              <AlertDescription>
                {t("organization-dialog.name_error_text")}
              </AlertDescription>
            </Alert>
          )}
          <div className="flex justyfiy-left items-center my-4">
            <Label className="mr-4 ml-2">Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => {
                onNameChange(e.target.value);
              }}
              placeholder="New Organization"
              className="max-w-1/2"
            />
          </div>
          {showAlert && (
            <Alert className="mt-2" variant="destructive">
              <AlertCircleIcon />
              <AlertTitle>
                {t("organization-dialog.email_error_header")}
              </AlertTitle>
              <AlertDescription>
                {t("organization-dialog.email_error_text")}
              </AlertDescription>
            </Alert>
          )}
          <div>
            <DataTableUsers
              columns={getUserColumns(handleRoleChange, handleUserDelete)}
              data={users}
              onAdd={handleAddNewUser}
            />
          </div>

          <DialogFooter>
            <Button type="submit" onClick={onSave}>
              {t("save_changes")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <AlertDialog open={showLeaveConfirm} onOpenChange={setShowLeaveConfirm}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center">
              <OctagonAlert size={20} className="text-red-500 mr-2" />
              {t("confirmation_dialog.title")}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {t("confirmation_dialog.unsaved_text")}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{t("Back")}</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-white shadow-xs hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60"
              onClick={() => {
                setShowLeaveConfirm(false);
                onOpenChange(false); // close the main dialog
              }}
            >
              <LogOut className="text-white" />
              {t("Leave")}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
