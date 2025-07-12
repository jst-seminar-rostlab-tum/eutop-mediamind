import {
  Select,
  SelectContent,
  SelectGroup,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import { Label } from "~/components/ui/label";
import { Checkbox } from "~/components/ui/checkbox";
import { Button } from "~/components/ui/button";
import { SelectItem } from "@radix-ui/react-select";
import {
  RoleBadge,
  type RoleVariant,
} from "~/custom-components/dashboard/role-badge";
import { RotateCcw } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";

interface FilterBarProps {
  onFiltersChange: (filters: {
    showUpdatedOnly: boolean;
    selectedRole: string;
    selectedVisibility: string;
  }) => void;
}

export function FilterBar({ onFiltersChange }: FilterBarProps) {
  const [showUpdatedOnly, setShowUpdatedOnly] = useState(false);
  const [selectedRole, setSelectedRole] = useState<RoleVariant | "">("");
  const [selectedVisibility, setSelectedVisibility] = useState<
    RoleVariant | ""
  >("");

  const { t } = useTranslation();

  const isRoleDefault = selectedRole === "";
  const isVisibilityDefault = selectedVisibility === "";

  const handleFilterChange = (
    newShowUpdatedOnly?: boolean,
    newSelectedRole?: string,
    newSelectedVisibility?: string,
  ) => {
    const updatedFilters = {
      showUpdatedOnly: newShowUpdatedOnly ?? showUpdatedOnly,
      selectedRole: newSelectedRole ?? selectedRole,
      selectedVisibility: newSelectedVisibility ?? selectedVisibility,
    };

    onFiltersChange(updatedFilters);
  };

  const handleShowUpdatedChange = (checked: boolean) => {
    setShowUpdatedOnly(checked);
    handleFilterChange(checked);
  };

  const handleRoleChange = (value: RoleVariant) => {
    setSelectedRole(value);
    handleFilterChange(undefined, value);
  };

  const handleVisibilityChange = (value: RoleVariant) => {
    setSelectedVisibility(value);
    handleFilterChange(undefined, undefined, value);
  };

  const resetRole = () => {
    setSelectedRole("");
    handleFilterChange(undefined, "");
  };

  const resetVisibility = () => {
    setSelectedVisibility("");
    handleFilterChange(undefined, undefined, "");
  };

  return (
    <div className="flex gap-5">
      <div className="flex items-center gap-3">
        <Label htmlFor="updated" className={"font-normal text-gray-600"}>
          {t("dashboard.only_updated")}
        </Label>
        <Checkbox
          id="updated"
          checked={showUpdatedOnly}
          onCheckedChange={handleShowUpdatedChange}
        />
      </div>

      <div className="flex items-center gap-2">
        <Select value={selectedRole} onValueChange={handleRoleChange}>
          <SelectTrigger className="w-[180px] rounded-lg">
            <SelectValue placeholder={<RoleBadge variant={"ownership"} />}>
              {selectedRole && <RoleBadge variant={selectedRole} />}
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>{t("role-badge.ownership")}</SelectLabel>
              <SelectItem value="owner" className={"py-1"}>
                <RoleBadge variant={"owner"} />
              </SelectItem>
              <SelectItem value="editor" className={"py-1"}>
                <RoleBadge variant={"editor"} />
              </SelectItem>
              <SelectItem value="reader" className={"py-1"}>
                <RoleBadge variant={"reader"} />
              </SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>
        <Button
          variant="outline"
          size="sm"
          onClick={resetRole}
          disabled={isRoleDefault}
          className="h-9 w-9 rounded-lg"
        >
          <RotateCcw className="h-4 w-4" />
        </Button>
      </div>

      <div className="flex items-center gap-2">
        <Select
          value={selectedVisibility}
          onValueChange={handleVisibilityChange}
        >
          <SelectTrigger className="w-[180px] rounded-lg">
            <SelectValue placeholder={<RoleBadge variant={"visibility"} />}>
              {selectedVisibility && <RoleBadge variant={selectedVisibility} />}
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>{t("role-badge.visibility")}</SelectLabel>
              <SelectItem value="public" className={"py-1"}>
                <RoleBadge variant={"public"} />
              </SelectItem>
              <SelectItem value="shared" className={"py-1"}>
                <RoleBadge variant={"shared"} />
              </SelectItem>
              <SelectItem value="private" className={"py-1"}>
                <RoleBadge variant={"private"} />
              </SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>
        <Button
          variant="outline"
          size="sm"
          onClick={resetVisibility}
          disabled={isVisibilityDefault}
          className="h-9 w-9 p-0 rounded-lg"
        >
          <RotateCcw className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
