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

export interface GeneralProps {
  profile: Profile;
  setProfile: (profile: Profile) => void;
}

export function General({ profile, setProfile }: GeneralProps) {
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

  const [open, setOpen] = React.useState(false);

  const selectedUser = users.find((user) => user.id === profile.owner_id);
  const selectedUserLabel = selectedUser
    ? `${selectedUser.first_name} ${selectedUser.last_name}`
    : t("general.select_user");

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
                            setProfile({ ...profile, owner_id: currentValue });
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

      <Separator />

      <h2 className="font-bold pt-3 pb-3">{t("general.visibility")}</h2>
      <div className="flex gap-3 items-center pb-3">
        <Label className="text-gray-400 font-normal">
          {t("general.public")}
        </Label>
        <Switch
          checked={profile.is_public}
          onCheckedChange={(e) => setProfile({ ...profile, is_public: e })}
        />
      </div>
      <Label className="text-gray-400 font-light pb-3">
        {t("general.public_text")}
      </Label>

      <Separator />

      <h2 className="font-bold pt-3 pb-3">{t("general.language")}</h2>
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

      <Separator />
    </div>
  );
}
