import {
  ArrowDownNarrowWide,
  Award,
  CalendarFold,
  ChevronDownIcon,
  Search,
  StickyNote,
  Tag,
} from "lucide-react";
import { Card, CardTitle } from "~/components/ui/card";
import { Input } from "~/components/ui/input";
import { Label } from "~/components/ui/label";
import { ScrollArea } from "~/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import { Checkbox } from "~/components/ui/checkbox";
import { Button } from "~/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "~/components/ui/popover";
import { Calendar } from "~/components/ui/calendar";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import i18n from "~/i18n";

interface SidebarFilterProps {
  sortBy: "relevance" | "date";
  setSortBy: (value: "relevance" | "date") => void;

  selectedSources: string[];
  setSelectedSources: React.Dispatch<React.SetStateAction<string[]>>;
  searchSources: string;
  setSearchSources: (value: string) => void;
  Sources: {
    id: string;
    name: string;
    is_subscribed: boolean;
  }[];

  selectedTopics: string[];
  setSelectedTopics: React.Dispatch<React.SetStateAction<string[]>>;
  searchTopics: string;
  setSearchTopics: (value: string) => void;
  Topics: {
    id: string;
    name: string;
    keywords: string[];
  }[];

  fromDate?: Date;
  setFromDate: React.Dispatch<React.SetStateAction<Date | undefined>>;
  toDate?: Date;
  setToDate: React.Dispatch<React.SetStateAction<Date | undefined>>;
}

export function SidebarFilter({
  sortBy,
  setSortBy,
  selectedSources,
  setSelectedSources,
  searchSources,
  setSearchSources,
  Sources,
  selectedTopics,
  setSelectedTopics,
  searchTopics,
  setSearchTopics,
  Topics,
  fromDate,
  setFromDate,
  toDate,
  setToDate,
}: SidebarFilterProps) {
  const [openFromDate, setOpenFromDate] = useState(false);
  const [openToDate, setOpenToDate] = useState(false);

  const { t } = useTranslation();

  const filteredSources = Sources.filter((source) =>
    source.name.toLowerCase().includes(searchSources.toLowerCase()),
  );

  const filteredTopics = Topics.filter((topic) =>
    topic.name.toLowerCase().includes(searchTopics.toLowerCase()),
  );

  return (
    <Card className="p-5 gap-4">
      <CardTitle className="mt-2 flex items-center gap-2">
        <ArrowDownNarrowWide /> {t("search_profile.Sorting")}
      </CardTitle>
      <Select
        value={sortBy}
        onValueChange={(value) => setSortBy(value as "relevance" | "date")}
      >
        <SelectTrigger className="w-full">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="relevance">
            <Award /> {t("search_profile.Relevance")}
          </SelectItem>
          <SelectItem value="date">
            <CalendarFold /> {t("search_profile.Date")}
          </SelectItem>
        </SelectContent>
      </Select>

      <CardTitle className="mt-4 flex items-center gap-2">
        <StickyNote /> {t("search_profile.Sources")}
      </CardTitle>
      <div className="relative w-full flex">
        <Input
          placeholder={t("Search") + " " + t("search_profile.Sources")}
          value={searchSources}
          onChange={(e) => setSearchSources(e.target.value)}
        />
        <Search
          size={20}
          className="absolute right-3 top-2 text-muted-foreground"
        />
      </div>
      <ScrollArea className="h-40 rounded-md border p-2">
        {filteredSources.map((source) => (
          <div key={source.id} className="flex items-center gap-2 p-2">
            <Checkbox
              id={source.id}
              checked={selectedSources.includes(source.id)}
              onCheckedChange={(checked) => {
                setSelectedSources((prev) =>
                  checked
                    ? [...prev, source.id]
                    : prev.filter((s) => s !== source.id),
                );
              }}
            />
            <Label>{source.name}</Label>
          </div>
        ))}
      </ScrollArea>

      <CardTitle className="mt-4 flex items-center gap-2">
        <Tag /> {t("search_profile.Topics")}
      </CardTitle>
      <div className="relative w-full flex">
        <Input
          placeholder={t("Search") + " " + t("search_profile.Topics")}
          value={searchTopics}
          onChange={(e) => setSearchTopics(e.target.value)}
        />
        <Search
          size={20}
          className="absolute right-3 top-2 text-muted-foreground"
        />
      </div>
      <ScrollArea className="h-40 rounded-md border p-2">
        {filteredTopics.map((topic) => (
          <div key={topic.id} className="flex items-center gap-2 p-2">
            <Checkbox
              id={topic.id}
              checked={selectedTopics.includes(topic.id)}
              onCheckedChange={(checked) => {
                setSelectedTopics((prev) =>
                  checked
                    ? [...prev, topic.id]
                    : prev.filter((t) => t !== topic.id),
                );
              }}
            />
            <Label>{topic.name}</Label>
          </div>
        ))}
      </ScrollArea>

      <CardTitle className="mt-4 flex items-center gap-2">
        <CalendarFold /> {t("search_profile.Date")}
      </CardTitle>
      <div className="flex mx-2 flex-wrap gap-y-4 mb-2">
        <div className="flex">
          <Label htmlFor="date" className="pr-2">
            {t("search_profile.From")}
          </Label>
          <Popover open={openFromDate} onOpenChange={setOpenFromDate}>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                id="date"
                className="justify-between font-normal"
              >
                {fromDate ? fromDate.toLocaleDateString() : "Select date"}
                <ChevronDownIcon />
              </Button>
            </PopoverTrigger>
            <PopoverContent
              className="w-auto overflow-hidden p-0"
              align="start"
            >
              <Calendar
                mode="single"
                selected={fromDate}
                captionLayout="dropdown"
                onSelect={(date) => setFromDate(date)}
              />
            </PopoverContent>
          </Popover>
        </div>

        <div className={i18n.language == "de" ? "flex ml-2" : "flex ml-4"}>
          <Label htmlFor="date" className="pr-2">
            {t("search_profile.To")}
          </Label>
          <Popover open={openToDate} onOpenChange={setOpenToDate}>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                id="date"
                className="justify-between font-normal"
              >
                {toDate ? toDate.toLocaleDateString() : "Select date"}
                <ChevronDownIcon />
              </Button>
            </PopoverTrigger>
            <PopoverContent
              className="w-auto overflow-hidden p-0"
              align="start"
            >
              <Calendar
                mode="single"
                selected={toDate}
                captionLayout="dropdown"
                onSelect={(date) => setToDate(date)}
              />
            </PopoverContent>
          </Popover>
        </div>
      </div>
    </Card>
  );
}
