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

interface SidebarFilterProps {
  sortBy: "relevance" | "date";
  setSortBy: (value: "relevance" | "date") => void;

  selectedSources: string[];
  setSelectedSources: React.Dispatch<React.SetStateAction<string[]>>;
  searchSources: string;
  setSearchSources: (value: string) => void;
  uniqueSources: string[];

  selectedTopics: string[];
  setSelectedTopics: React.Dispatch<React.SetStateAction<string[]>>;
  searchTopics: string;
  setSearchTopics: (value: string) => void;
  uniqueTopics: string[];

  fromDate?: Date;
  setFromDate: (value?: Date) => void;
  toDate?: Date;
  setToDate: (value?: Date) => void;
}

export function SidebarFilter({
  sortBy,
  setSortBy,
  selectedSources,
  setSelectedSources,
  searchSources,
  setSearchSources,
  uniqueSources,
  selectedTopics,
  setSelectedTopics,
  searchTopics,
  setSearchTopics,
  uniqueTopics,
  fromDate,
  setFromDate,
  toDate,
  setToDate,
}: SidebarFilterProps) {
  const [openFromDate, setOpenFromDate] = useState(false);
  const [openToDate, setOpenToDate] = useState(false);

  const filteredSources = uniqueSources.filter((source) =>
    source.toLowerCase().includes(searchSources.toLowerCase()),
  );

  const filteredTopics = uniqueTopics.filter((topic) =>
    topic.toLowerCase().includes(searchTopics.toLowerCase()),
  );

  return (
    <Card className="p-5 gap-4">
      <CardTitle className="mt-2 flex items-center gap-2">
        <ArrowDownNarrowWide /> Sorting
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
            <Award /> Relevance
          </SelectItem>
          <SelectItem value="date">
            <CalendarFold /> Date
          </SelectItem>
        </SelectContent>
      </Select>

      <CardTitle className="mt-4 flex items-center gap-2">
        <StickyNote /> Sources
      </CardTitle>
      <div className="relative w-full flex">
        <Input
          placeholder="Search sources"
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
          <div key={source} className="flex items-center gap-2 p-2">
            <Checkbox
              id={source}
              checked={selectedSources.includes(source)}
              onCheckedChange={(checked) => {
                setSelectedSources((prev) =>
                  checked
                    ? [...prev, source]
                    : prev.filter((s) => s !== source),
                );
              }}
            />
            <Label>{source}</Label>
          </div>
        ))}
      </ScrollArea>

      <CardTitle className="mt-4 flex items-center gap-2">
        <Tag /> Topics
      </CardTitle>
      <div className="relative w-full flex">
        <Input
          placeholder="Search topics"
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
          <div key={topic} className="flex items-center gap-2 p-2">
            <Checkbox
              id={topic}
              checked={selectedTopics.includes(topic)}
              onCheckedChange={(checked) => {
                setSelectedTopics((prev) =>
                  checked ? [...prev, topic] : prev.filter((t) => t !== topic),
                );
              }}
            />
            <Label>{topic}</Label>
          </div>
        ))}
      </ScrollArea>

      <CardTitle className="mt-4 flex items-center gap-2">
        <CalendarFold /> Date
      </CardTitle>
      <div className="flex mx-2 flex-wrap gap-y-4 mb-2">
        <div className="flex">
          <Label htmlFor="date" className="pr-2">
            From
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

        <div className="flex ml-4">
          <Label htmlFor="date" className="pr-2">
            To
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
