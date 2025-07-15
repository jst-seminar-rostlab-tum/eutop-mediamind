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
import { useEffect, useMemo, useState } from "react";
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
import type { MediamindUser, Organization } from "types/model";
import { cloneDeep, isEqual } from "lodash-es";
import type { Row } from "@tanstack/react-table";
import { useQuery } from "types/api";
import { toast } from "sonner";
import { UserTableSkeleton } from "../skeleton";

type Props = {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  isEdit: boolean;
  orga: Organization | null;
  onSave: (orga: Organization) => void;
};

export type TableUser = {
  id: string;
  email: string;
  username: string;
  role: "maintainer" | "member";
};

export function OrganizationDialog({
  open,
  onOpenChange,
  isEdit,
  orga,
  onSave,
}: Props) {
  const { t } = useTranslation();

  const FormSchema = z.object({
    name: z
      .string()
      .min(1, { message: t("organization-dialog.name_required") })
      .max(20, { message: t("organization-dialog.name_length") })
      .regex(/^[a-zA-Z0-9 ]+$/, {
        message: t("organization-dialog.name_regex"),
      }),
  });

  type FormValues = z.infer<typeof FormSchema>;

  const {
    data: userData,
    isLoading: usersLoading,
    error: usersError,
  } = useQuery("/api/v1/users");

  if (usersError) {
    toast(t("organization-dialog.users_error"));
  }

  const allUsers: MediamindUser[] = useMemo(() => {
    if (!userData) return [];
    return Array.isArray(userData) ? userData : [userData];
  }, [userData]);

  const [showLeaveConfirm, setShowLeaveConfirm] = useState(false);
  const [tableUsers, setTableUsers] = useState<TableUser[]>([]);

  // initial orga for creation mode
  const initialOrga = {
    name: "",
    email: "",
    pdf_as_link: true,
    id: "",
    users: [],
    subscriptions: [],
  };

  // set edited orga either to orga for edit or initialOrga for create
  const editedOrga = useMemo(() => {
    return cloneDeep(isEdit && orga ? orga : initialOrga);
  }, [isEdit, orga]);

  // prepare user data for table
  useEffect(() => {
    if (!open) return;

    if (isEdit && orga?.users) {
      const mappedUsers: TableUser[] = orga.users.map((user) => ({
        id: user.id ?? "",
        email: user.email,
        username: `${user.first_name} ${user.last_name}`,
        role: user.role,
      }));

      setTableUsers(mappedUsers);
    } else {
      setTableUsers([]); // in creation mode
    }
  }, [open]);

  const handleRoleChange = (
    index: number,
    newRole: "maintainer" | "member",
  ) => {
    setTableUsers((prev) =>
      prev.map((user, i) => (i === index ? { ...user, role: newRole } : user)),
    );
  };

  const handleUserDelete = (index: number) => {
    setTableUsers((prev) => prev.filter((_, i) => i !== index));
  };

  const handleBunchDelete = (selectedRows: Row<TableUser>[]) => {
    const usersToRemove = selectedRows.map((row) => row.original);
    setTableUsers((prev) =>
      prev.filter((user) => !usersToRemove.some((r) => r.id === user.id)),
    );
  };

  const handleAddNewUser = (email: string) => {
    const user = allUsers.find((user) => user.email === email);
    if (!user) {
      return;
    }
    // prevent duplicates
    if (tableUsers.some((u) => u.email === user.email)) {
      toast.error(t("organization-dialog.user_already_added"));
      return;
    }
    // create new table user
    const tableUser: TableUser = {
      id: user.id,
      email: user.email,
      username: `${user.first_name} ${user.last_name}`,
      role: user.role ?? "member", // default to member
    };
    setTableUsers((prev) => [...prev, tableUser]);
  };

  // prepare data and call onSave
  const onSubmit = (values: FormValues) => {
    const updatedOrga = {
      ...editedOrga,
      name: values.name.trim(),
      users: tableUsers
        .map((tableUser) => {
          // get fullUser by id
          const fullUser = allUsers.find((u) => u.id === tableUser.id);
          if (!fullUser) return null;
          return {
            ...fullUser,
            // take role from tableUser
            role: tableUser.role,
            gender: fullUser.gender ?? null,
          };
        })
        .filter((u): u is NonNullable<typeof u> => u !== null), // Remove unmatched users
    };

    onSave(updatedOrga);
  };

  const form = useForm<FormValues>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      name: editedOrga.name,
    },
  });

  useEffect(() => {
    form.reset({ name: editedOrga.name });
  }, [editedOrga, open]);

  const checkEqual = (isEdit: boolean) => {
    const base = isEdit ? (orga as Organization) : initialOrga;

    const updated = {
      ...base,
      name: form.getValues().name.trim(),
      users: tableUsers
        .map((tableUser) => {
          const fullUser = allUsers.find((u) => u.email === tableUser.email);
          if (!fullUser) return null;
          return {
            id: fullUser.id,
            clerk_id: fullUser.clerk_id,
            email: fullUser.email,
            first_name: fullUser.first_name,
            last_name: fullUser.last_name,
            is_superuser: fullUser.is_superuser,
            language: fullUser.language,
            gender: fullUser.gender,
            organization_id: fullUser.organization_id,
            breaking_news: fullUser.breaking_news,
            // get role form table user to check if edited
            role: tableUser.role,
          };
        })
        .filter((u): u is NonNullable<typeof u> => u !== null),
    };
    return isEqual(updated, base);
  };

  return (
    <>
      <Dialog
        open={open}
        onOpenChange={(isOpen) => {
          if (!checkEqual(isEdit)) {
            // if changes, show AlertDialog
            setShowLeaveConfirm(true);
          } else {
            onOpenChange(isOpen);
          }
        }}
      >
        <DialogContent className="min-w-[850px]">
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
                    <FormItem className="flex items-center">
                      <FormLabel>{t("organization-dialog.Name")}</FormLabel>
                      <FormControl>
                        <Input
                          placeholder={t(
                            "organization-dialog.New_Organization",
                          )}
                          {...field}
                        />
                      </FormControl>
                      <FormMessage className="pl-2 w-full items-center " />
                    </FormItem>
                  )}
                />
              </div>
              <div>
                {usersLoading ? (
                  <UserTableSkeleton />
                ) : (
                  <DataTableUsers
                    columns={getUserColumns(
                      t,
                      handleRoleChange,
                      handleUserDelete,
                    )}
                    data={tableUsers}
                    onAdd={handleAddNewUser}
                    users={allUsers}
                    onBunchDelete={handleBunchDelete}
                  />
                )}
              </div>

              <DialogFooter>
                <Button className="mt-2" variant={"secondary"} type="submit">
                  {t("save_changes")}
                </Button>
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
          onOpenChange(false);
        }}
      />
    </>
  );
}
