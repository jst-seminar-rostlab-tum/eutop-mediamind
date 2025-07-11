import {
  Select,
  SelectContent,
  SelectGroup,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import { RoleBadge } from "~/custom-components/dashboard/role-badge";
import { SelectItem } from "@radix-ui/react-select";
import { Button } from "~/components/ui/button";
import { RotateCcw } from "lucide-react";
import { useTranslation } from "react-i18next";

interface ReportFilterBarProps {
  language: string | undefined;
  onLanguageChange: (value: string) => void;
  onReset: () => void;
}

export function ReportFilterBar({
  language,
  onLanguageChange,
  onReset,
}: ReportFilterBarProps) {
  const { t } = useTranslation();
  return (
    <div className="flex items-center gap-2">
      <Select value={language} onValueChange={onLanguageChange}>
        <SelectTrigger className="w-[180px] rounded-xl">
          <SelectValue placeholder={<RoleBadge variant={"language"} />}>
            {language ? (
              <RoleBadge variant={language as "de" | "en"} />
            ) : (
              <RoleBadge variant="language" />
            )}
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            <SelectLabel>{t("role-badge.language")}</SelectLabel>
            <SelectItem value="de" className={"py-1"}>
              <RoleBadge variant={"de"} />
            </SelectItem>
            <SelectItem value="en" className={"py-1"}>
              <RoleBadge variant={"en"} />
            </SelectItem>
          </SelectGroup>
        </SelectContent>
      </Select>
      <Button
        variant="outline"
        size="sm"
        onClick={onReset}
        disabled={!language}
        className="h-9 w-9 p-0 rounded-xl"
      >
        <RotateCcw className="h-4 w-4" />
      </Button>
    </div>
  );
}
