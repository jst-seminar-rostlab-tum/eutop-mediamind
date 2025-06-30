import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "~/components/ui/dialog";
import { Input } from "~/components/ui/input";
import { Button } from "~/components/ui/button";
import { getUserColumns } from "../columns";
import type { User } from "../types";
import React, { useEffect } from "react";

import { DataTableUsers } from "~/custom-components/admin-settings/data-table-users";
import { useTranslation } from "react-i18next";
import { ConfirmationDialog } from "~/custom-components/confirmation-dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "~/components/ui/form";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

const FormSchema = z.object({
  name: z
    .string()
    .min(1, { message: "Name is required." })
    .max(20, { message: "Max length is 20 characters." })
    .regex(/^[a-zA-Z0-9]+$/, {
      message: "Only letters and numbers are allowed.",
    }),
});

type FormValues = z.infer<typeof FormSchema>;

type Props = {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  isEdit: boolean;
  users: User[];
  setUsers: (users: User[]) => void;
  onSave: (data: FormValues) => void;
  unsavedEdits: boolean;
  setUnsavedEdits: (val: boolean) => void;
  initialOrgaName: string;
};

export function OrganizationDialog({
  open,
  onOpenChange,
  isEdit,
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

  const form = useForm<FormValues>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      name: initialOrgaName,
    },
  });

  useEffect(() => {
    form.reset({ name: initialOrgaName });
  }, [initialOrgaName, open]);

  return (
    <>
      <Dialog
        open={open}
        onOpenChange={(isOpen) => {
          const nameChanged = initialOrgaName !== form.getValues("name");

          if (!isOpen && (unsavedEdits || nameChanged)) {
            setShowLeaveConfirm(true); // show AlertDialog instead
          } else {
            onOpenChange(isOpen); // normal open/close
          }
        }}
      >
        <DialogContent className="min-w-[700px]">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSave)} className="space-y-4">
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
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem className="flex">
                      <FormLabel>{t("organization-dialog.Name")}</FormLabel>
                      <FormControl>
                        <Input
                          placeholder={t(
                            "organization-dialog.New_Organization",
                          )}
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
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
                <Button type="submit">{t("save_changes")}</Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      <ConfirmationDialog
        open={showLeaveConfirm}
        onOpenChange={setShowLeaveConfirm}
        dialogType="leave"
        action={() => {
          onOpenChange(false); // closes organization-dialog
        }}
      />
    </>
  );
}
