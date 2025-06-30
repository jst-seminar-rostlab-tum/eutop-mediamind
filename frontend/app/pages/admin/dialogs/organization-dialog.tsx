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
import React from "react";

import { DataTableUsers } from "~/custom-components/admin-settings/data-table-users";
import { useTranslation } from "react-i18next";
import { ConfirmationDialog } from "~/custom-components/confirmation-dialog";
import { cn } from "~/lib/utils";

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
          <div className="flex justyfiy-left items-center my-4">
            <Label className="mr-4 ml-2">Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => {
                onNameChange(e.target.value);
              }}
              placeholder="New Organization"
              className={cn(
                "max-w-1/2",
                name == "" &&
                  open &&
                  "border-2 border-destructive focus-visible:ring-destructive focus-visible:border-destructive",
              )}
            />
          </div>
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

      <ConfirmationDialog
        open={showLeaveConfirm}
        onOpenChange={setShowLeaveConfirm}
        dialogType="leave"
        action={() => {
          onOpenChange(false); // closes organization dialog dialog
        }}
      />
    </>
  );
}
