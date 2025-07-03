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
import { useEffect, useState } from "react";
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
import type { Organization } from "types/model";
import { cloneDeep, isEqual } from "lodash-es";

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
  orga: Organization;
  onSave: (data: FormValues) => void;
};

type TableUser = {
  email: string;
  name: string;
  role: "admin" | "user";
};

export function OrganizationDialog({
  open,
  onOpenChange,
  isEdit,
  orga,
  onSave,
}: Props) {
  const [showLeaveConfirm, setShowLeaveConfirm] = useState(false);
  const [tableUsers, setTableUsers] = useState<TableUser[]>([]);

  const initialOrga: Organization = {
    name: "",
    email: "",
    id: "",
    users: [],
  };

  const { t } = useTranslation();

  const [editedOrga, setEditedOrga] = useState<Organization>(
    cloneDeep(orga ?? initialOrga),
  );

  // prepare user data
  useEffect(() => {
    if (!orga?.users) return;

    const mappedUsers: TableUser[] = orga.users.map((user) => ({
      email: user.email,
      name: user.first_name + " " + user.last_name,
      role: user.is_superuser ? "admin" : "user",
    }));

    setTableUsers(mappedUsers);
  }, [orga]);

  const handleRoleChange = (index: number, newRole: "admin" | "user") => {
    setTableUsers((prev) =>
      prev.map((user, i) => (i === index ? { ...user, role: newRole } : user)),
    );
  };

  const handleUserDelete = (index: number) => {
    setTableUsers((prev) => prev.filter((_, i) => i !== index));
  };

  const handleAddNewUser = (email: string) => {
    // merge user rights table first
  };

  // prepare data
  const onSubmit = (values: FormValues) => {
    const updatedOrga: Organization = {
      ...editedOrga,
      name: values.name.trim(),

      users: tableUsers.map((user) => ({
        // get the actual user for this table users email
        email: "",
        first_name: "",
        last_name: "",
        is_superuser: user.role === "admin",
        language: "en", // default or get from somewhere
        clerk_id: "",
      })),
    };

    onSave(updatedOrga);
  };

  // react hook form
  const form = useForm<FormValues>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      name: orga.name,
    },
  });

  useEffect(() => {
    form.reset({ name: orga.name });
  }, [orga, open]);

  return (
    <>
      <Dialog
        open={open}
        onOpenChange={(isOpen) => {
          if (isEdit) {
            // nothing changed while editing
            if (isEqual(orga, editedOrga)) {
              onOpenChange(isOpen); // normal open/close
            } else {
              setShowLeaveConfirm(true); // show AlertDialog instead
            }
          } else {
            // nothing changed while creating
            if (isEqual(initialOrga, editedOrga)) {
              onOpenChange(isOpen); // normal open/close
            } else {
              setShowLeaveConfirm(true); // show AlertDialog instead
            }
          }
        }}
      >
        <DialogContent className="min-w-[700px]">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
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
                  data={tableUsers}
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
