import { Label } from "~/components/ui/label";
import { Switch } from "~/components/ui/switch";
import { Separator } from "~/components/ui/separator";
import { Button } from "~/components/ui/button";
import { Check, ChevronsUpDown } from "lucide-react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "~/components/ui/popover";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "~/components/ui/command";
import {
  Select,
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValue,
} from "~/components/ui/select";
import * as React from "react";
import { cn } from "~/lib/utils";
import { useQuery } from "../../../../types/api";
import type { MediamindUser, Profile } from "../../../../types/model";
import { useEffect } from "react";
import { toast } from "sonner";
import { useTranslation } from "react-i18next";
import { DataTableUsers } from "~/custom-components/admin-settings/data-table-users";
import { getUserColumns } from "./columns";
import type { Row } from "@tanstack/react-table";

export type UserWithRole = {
  id: string;
  email: string;
  username: string;
  rights: "read" | "edit";
};

export interface GeneralProps {
  profile: Profile;
  setProfile: (profile: Profile) => void;
}

export function General({ profile, setProfile }: GeneralProps) {
  const [open, setOpen] = React.useState(false);
  const [usersWithRoles, setUsersWithRoles] = React.useState<UserWithRole[]>(
    [],
  );

  const { data: userData, isLoading, error } = useQuery("/api/v1/users");
  const { t } = useTranslation();

  useEffect(() => {
    if (error) {
      toast.error(t("general.user_error"));
    }
  }, [error]);

  const users: MediamindUser[] = React.useMemo(() => {
    if (!userData) return [];
    return Array.isArray(userData) ? userData : [userData];
  }, [userData]);

  const selectedUser = users.find((user) => user.id === profile.owner_id);
  const selectedUserLabel = selectedUser
    ? `${selectedUser.first_name} ${selectedUser.last_name}`
    : t("general.select_user");

  // match read and write ids with users emails and rights
  function getUsersWithRole(
    profileUserIds: string[],
    orgaUsers: MediamindUser[],
    rights: "read" | "edit",
  ): UserWithRole[] {
    const userMap = new Map(orgaUsers.map((u) => [u.id, u]));

    return profileUserIds
      .map((id) => {
        const user = userMap.get(id)!;
        if (!user) return null;
        return {
          id: user.id,
          email: user.email,
          username: user.first_name + " " + user.last_name,
          rights,
        };
      })
      .filter((u): u is UserWithRole => u !== null);
  }

  // initialize users with roles for the table
  useEffect(() => {
    if (!users.length) return;

    const readUsers = getUsersWithRole(
      profile.can_read_user_ids,
      users,
      "read",
    );
    const editUsers = getUsersWithRole(
      profile.can_edit_user_ids,
      users,
      "edit",
    );

    setUsersWithRoles([...readUsers, ...editUsers]);
  }, [users, profile.can_read_user_ids, profile.can_edit_user_ids]);

  console.log(usersWithRoles);

  // handle role change
  const handleRoleChange = (index: number, newRights: "read" | "edit") => {
    const user = usersWithRoles[index];
    if (!user) return;

    const userId = user.id;

    // update local state for table
    setUsersWithRoles((prev) =>
      prev.map((user, i) =>
        i === index ? { ...user, rights: newRights } : user,
      ),
    );

    // Clean out userId from both rights
    const cleanedReadIds = profile.can_read_user_ids.filter(
      (id) => id !== userId,
    );
    const cleanedEditIds = profile.can_edit_user_ids.filter(
      (id) => id !== userId,
    );

    // create updated profile with new user's rights
    const updatedProfile = {
      ...profile,
      can_read_user_ids:
        newRights === "read" ? [...cleanedReadIds, userId] : cleanedReadIds,
      can_edit_user_ids:
        newRights === "edit" ? [...cleanedEditIds, userId] : cleanedEditIds,
    };

    // set profile to updated profile
    setProfile(updatedProfile);
  };

  // crate user with rights object form selected email to add
  const createAndAddNewUser = (email: string) => {
    // find user with selected email
    const user = users.find((u) => u.email === email);
    if (!user) return;

    // check for duplicates
    const alreadyExists = usersWithRoles.some((u) => u.id === user.id);
    if (alreadyExists) {
      toast.error(t("general.user_already_added"));
      return;
    }

    const newUser: UserWithRole = {
      id: user.id,
      email: user.email,
      username: user.first_name + user.last_name,
      rights: "read", // default rights: read
    };

    // update local state
    setUsersWithRoles((prev) => [...prev, newUser]);

    // add new id to read ids
    if (!profile.can_read_user_ids.includes(user.id)) {
      setProfile({
        ...profile,
        can_read_user_ids: [...profile.can_read_user_ids, user.id],
      });
    }
  };

  const handleUserDelete = (index: number) => {
    //get user with this index
    const userToRemove = usersWithRoles[index];
    if (!userToRemove) return;

    // update local state
    setUsersWithRoles((prev) => prev.filter((_, i) => i !== index));

    // update profile
    setProfile({
      ...profile,
      can_read_user_ids: profile.can_read_user_ids.filter(
        (id) => id !== userToRemove.id,
      ),
      can_edit_user_ids: profile.can_edit_user_ids.filter(
        (id) => id !== userToRemove.id,
      ),
    });
  };

  const handleBunchDelete = (selectedRows: Row<UserWithRole>[]) => {
    const usersToRemove = selectedRows.map((row) => row.original);

    // Update usersWithRoles
    setUsersWithRoles((prev) =>
      prev.filter((user) => !usersToRemove.some((r) => r.id === user.id)),
    );

    // Update profile
    const newReadIds = profile.can_read_user_ids.filter(
      (id) => !usersToRemove.some((user) => user.id === id),
    );
    const newEditIds = profile.can_edit_user_ids.filter(
      (id) => !usersToRemove.some((user) => user.id === id),
    );

    setProfile({
      ...profile,
      can_read_user_ids: newReadIds,
      can_edit_user_ids: newEditIds,
    });
  };

  const languages = [
    { value: "en", label: "English" },
    { value: "de", label: "Deutsch" },
  ];

  return (
    <div>
      <h2 className="font-bold pt-3 pb-3">{t("general.ownership")}</h2>
      <Label className="text-gray-400 font-normal pb-3">
        {t("general.ownership_text")}
      </Label>
      <div className="pb-3">
        <Popover open={open} onOpenChange={setOpen}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              role="combobox"
              aria-expanded={open}
              className=" justify-between"
              disabled={isLoading}
            >
              {selectedUserLabel}
              <ChevronsUpDown className="opacity-50" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-full p-0">
            <Command>
              <CommandInput
                placeholder={t("edit_profile.search_user")}
                className="h-9"
              />
              <CommandList>
                {isLoading ? (
                  <div className="p-4 text-sm text-center">
                    {t("edit_profile.loading")}
                  </div>
                ) : (
                  <>
                    <CommandEmpty>{t("edit_profile.no_user")}</CommandEmpty>
                    <CommandGroup>
                      {users.map((user) => (
                        <CommandItem
                          key={user.id}
                          value={user.id}
                          onSelect={(currentValue) => {
                            setProfile({
                              ...profile,
                              owner_id: currentValue,
                            });
                            setOpen(false);
                          }}
                        >
                          {`${user.first_name} ${user.last_name}`}
                          <Check
                            className={cn(
                              "ml-auto",
                              profile.owner_id === user.id
                                ? "opacity-100"
                                : "opacity-0",
                            )}
                          />
                        </CommandItem>
                      ))}
                    </CommandGroup>
                  </>
                )}
              </CommandList>
            </Command>
          </PopoverContent>
        </Popover>
      </div>

      <Separator className="my-2" />

      <h2 className="font-bold pt-3 pb-3">{t("general.visibility")}</h2>

      <Label className="text-gray-400 font-light pb-3">
        {t("general.public_text")}
      </Label>
      <div className="flex gap-3 items-center pb-3">
        <Label className="text-gray-400 font-normal">
          {t("general.public")}
        </Label>
        <Switch
          checked={profile.is_public}
          onCheckedChange={(e) => setProfile({ ...profile, is_public: e })}
        />
      </div>

      <Separator className="my-2" />

      <h2 className="font-bold pt-3 pb-3">{t("general.language")}</h2>
      <Label className="text-gray-400 font-light pb-3 leading-[120%]">
        {t("general.language_text")}
      </Label>
      <div className="pb-3">
        <Select
          value={profile.language}
          onValueChange={(value) => setProfile({ ...profile, language: value })}
        >
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder={t("general.select_language")} />
          </SelectTrigger>
          <SelectContent>
            {languages.map((lang) => (
              <SelectItem key={lang.value} value={lang.value}>
                {lang.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <Separator className="my-2" />

      <h2 className="font-bold pt-3 pb-3">{t("general.Users_header")}</h2>
      <Label className="text-gray-400 font-light pb-3 leading-[120%]">
        {t("general.users_text")}
      </Label>
      <div>
        <DataTableUsers
          columns={getUserColumns(handleRoleChange, handleUserDelete)}
          data={usersWithRoles}
          onAdd={createAndAddNewUser}
          users={users}
          onBunchDelete={handleBunchDelete}
        />
      </div>
    </div>
  );
}
