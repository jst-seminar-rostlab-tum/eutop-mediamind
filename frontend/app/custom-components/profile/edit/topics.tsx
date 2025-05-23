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

export function Topics({ profile }: { profile: Profile }) {
  const [selectedTopic, setSelectedTopic] = useState<string | undefined>(undefined);
  const selectedTopicKeywords = profile.topics.find((topic) => topic.name === selectedTopic)?.keywords || [];

  return (
    <div className="space-y-4">
        <Select onValueChange={(value) => setSelectedTopic(value)}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Select Topic" />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>Topics</SelectLabel>
              {profile.topics.map((topic) => (
                <SelectItem key={topic.name} value={topic.name}>{topic.name}</SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>

      {selectedTopic && (
        <KeywordField keywords={selectedTopicKeywords} />
      )}
      <div className={"flex justify-between"}>
        {selectedTopic && (
          <Button variant="outline">Delete "{selectedTopic}"</Button>
        )}
        <Button>Save Changes</Button>
      </div>

    </div>
  );
}
