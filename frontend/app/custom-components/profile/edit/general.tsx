import type { Profile } from "~/types/profile";
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

export interface GeneralProps {
  profile: Profile;
  setProfile: (profile: Profile) => void;
}

const users = [
  {
    value: "john.doe@example.com",
    label: "John Doe",
  },
  {
    value: "jane.smith@example.com",
    label: "Jane Smith",
  },
  {
    value: "contact@anotherdomain.org",
    label: "Contact Us",
  },
  {
    value: "alex.wilson@email.net",
    label: "Alex Wilson",
  },
];

export function General({ profile, setProfile }: GeneralProps) {
  const [open, setOpen] = React.useState(false);

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
            >
              {profile.owner
                ? users.find((user) => user.value === profile.owner)?.label
                : "Select user..."}
              <ChevronsUpDown className="opacity-50" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-[200px] p-0">
            <Command>
              <CommandInput placeholder="Search user..." className="h-9" />
              <CommandList>
                <CommandEmpty>No user found.</CommandEmpty>
                <CommandGroup>
                  {users.map((user) => (
                    <CommandItem
                      key={user.value}
                      value={user.value}
                      onSelect={(currentValue) => {
                        setProfile({ ...profile, owner: currentValue });
                        setOpen(false);
                      }}
                    >
                      {user.label}
                      <Check
                        className={cn(
                          "ml-auto",
                          profile.owner === user.value
                            ? "opacity-100"
                            : "opacity-0",
                        )}
                      />
                    </CommandItem>
                  ))}
                </CommandGroup>
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

      {profile.public && (
        <div>
          <h2 className={"font-bold pt-3 pb-3"}>Editability</h2>
          <div className={"flex gap-3"}>
            <Label className={"text-gray-400 font-normal pb-3"}>
              Profile can be edited by anyone
            </Label>
            <Switch
              checked={profile.editable}
              onCheckedChange={(e) => setProfile({ ...profile, editable: e })}
            />
          </div>
        </div>
      )}
    </div>
  );
}
