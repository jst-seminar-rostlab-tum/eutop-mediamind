import { Label } from "~/components/ui/label";
import { Switch } from "~/components/ui/switch";
import { Separator } from "~/components/ui/separator";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "~/components/ui/popover";
import { Button } from "~/components/ui/button";
import { Check, ChevronsUpDown } from "lucide-react";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "~/components/ui/command";
import * as React from "react";
import { cn } from "~/lib/utils";
import { useQuery } from "../../../../types/api";
import type { MediamindUser, Profile } from "../../../../types/model";
import { useEffect } from "react";
import { toast } from "sonner";

export interface GeneralProps {
  profile: Profile;
  setProfile: (profile: Profile) => void;
}

export function General({ profile, setProfile }: GeneralProps) {
  const { data: userData, isLoading, error } = useQuery("/api/v1/users");

  useEffect(() => {
    if (error) {
      toast.error("Failed to load users.");
    }
  }, [error]);

  const users: MediamindUser[] = React.useMemo(() => {
    if (!userData) {
      return [];
    }
    if (Array.isArray(userData)) {
      return userData;
    }
    return [userData];
  }, [userData]);

  const [open, setOpen] = React.useState(false);

  const selectedUser = users.find((user) => user.id === profile.owner);

  const selectedUserLabel = selectedUser
    ? `${selectedUser.first_name} ${selectedUser.last_name}`
    : "Select user...";

  return (
    <div>
      <h2 className={"font-bold pt-3 pb-3"}>Ownership</h2>
      <Label className={"text-gray-400 font-normal pb-3"}>
        Transfer ownership of the profile
      </Label>
      <div className="pb-3">
        <Popover open={open} onOpenChange={setOpen}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              role="combobox"
              aria-expanded={open}
              className="w-[200px] justify-between"
              disabled={isLoading}
            >
              {selectedUserLabel}
              <ChevronsUpDown className="opacity-50" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-[200px] p-0">
            <Command>
              <CommandInput placeholder="Search user..." className="h-9" />
              <CommandList>
                {isLoading ? (
                  <div className="p-4 text-sm text-center">Loading...</div>
                ) : (
                  <>
                    <CommandEmpty>No user found.</CommandEmpty>
                    <CommandGroup>
                      {users.map((user) => (
                        <CommandItem
                          key={user.id}
                          value={user.id}
                          onSelect={(currentValue) => {
                            setProfile({ ...profile, owner: currentValue });
                            setOpen(false);
                          }}
                        >
                          {`${user.first_name} ${user.last_name}`}
                          <Check
                            className={cn(
                              "ml-auto",
                              profile.owner === user.id
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

      <h2 className={"font-bold pt-3 pb-3"}>Visibility</h2>
      <div className={"flex gap-3 items-center pb-3"}>
        <Label className={"text-gray-400 font-normal"}>Public</Label>
        <Switch
          checked={profile.public}
          onCheckedChange={(e) => setProfile({ ...profile, public: e })}
        />
      </div>
      <Label className={"text-gray-400 font-light pb-3"}>
        A public profile can be viewed by anyone in your organization, while a
        private profile is only visible to you.
      </Label>

      <Separator />
    </div>
  );
}
