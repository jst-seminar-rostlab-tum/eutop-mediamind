import type { Profile } from "~/types/profile";
import { useState } from "react";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import { Button } from "~/components/ui/button";
import { KeywordField } from "~/custom-components/profile/edit/keyword-field";
import { Label } from "~/components/ui/label";
import { Input } from "~/components/ui/input";
import { Trash2 } from "lucide-react";

export function Topics({ profile }: { profile: Profile }) {
  const [selectedTopic, setSelectedTopic] = useState<string | undefined>(
    profile.topics.length > 0 ? profile.topics[0].name : undefined,
  );
  const selectedTopicKeywords =
    profile.topics.find((topic) => topic.name === selectedTopic)?.keywords ||
    [];

  return (
    <div>
      <h2 className={"font-bold pt-3 pb-3"}>Topics and Keywords</h2>
      <Label className={"text-gray-400 font-normal pb-4"}>
        Manage topics and keywords for news monitoring
      </Label>
      <div className="space-y-4">
        <div className={"flex gap-3"}>
          <Label>Topic:</Label>
          <Select
            value={selectedTopic}
            onValueChange={(value) => setSelectedTopic(value)}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select Topic" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectLabel>Topics</SelectLabel>
                {profile.topics.map((topic) => (
                  <SelectItem key={topic.name} value={topic.name}>
                    {topic.name}
                  </SelectItem>
                ))}
              </SelectGroup>
            </SelectContent>
          </Select>
          {selectedTopic && (
            <Button variant="destructive">
              <Trash2 />
              {selectedTopic}
            </Button>
          )}
          <Input
            placeholder={"+ Add topic"}
            className={"w-[180px] shadow-none ml-auto"}
          />
        </div>

        {selectedTopic && <KeywordField keywords={selectedTopicKeywords} />}
      </div>
    </div>
  );
}
