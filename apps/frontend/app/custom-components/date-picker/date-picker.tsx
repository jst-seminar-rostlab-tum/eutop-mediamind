import { ChevronDownIcon } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "~/components/ui/button";
import { Calendar } from "~/components/ui/calendar";
import { Label } from "~/components/ui/label";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "~/components/ui/popover";

interface DatePickerProps {
  startDate?: Date;
  endDate?: Date;
  setStartDate: (date: Date | undefined) => void;
  setEndDate: (date: Date | undefined) => void;
}

export const DatePicker = ({
  startDate,
  endDate,
  setStartDate,
  setEndDate,
}: DatePickerProps) => {
  const [openFromDate, setOpenFromDate] = useState(false);
  const [openToDate, setOpenToDate] = useState(false);
  const { t } = useTranslation();

  return (
    <div className="flex flex-wrap gap-y-4 mb-2 items-center">
      <div className="flex">
        <Popover open={openFromDate} onOpenChange={setOpenFromDate}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              id="date"
              className="justify-between font-normal"
            >
              {startDate ? startDate.toLocaleDateString() : t("select_date")}
              <ChevronDownIcon />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto overflow-hidden p-0" align="start">
            <Calendar
              mode="single"
              selected={startDate}
              captionLayout="dropdown"
              onSelect={(date) => setStartDate(date)}
            />
          </PopoverContent>
        </Popover>
      </div>
      <Label className={"px-1"}>-</Label>
      <div>
        <Popover open={openToDate} onOpenChange={setOpenToDate}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              id="date"
              className="justify-between font-normal"
            >
              {endDate ? endDate.toLocaleDateString() : t("select_date")}
              <ChevronDownIcon />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto overflow-hidden p-0" align="start">
            <Calendar
              mode="single"
              selected={endDate}
              captionLayout="dropdown"
              onSelect={(date) => setEndDate(date)}
            />
          </PopoverContent>
        </Popover>
      </div>
    </div>
  );
};
