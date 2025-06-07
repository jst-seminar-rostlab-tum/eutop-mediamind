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
import type { components } from "../../../../types/api-types-v1";
import { Sparkles, Trash2 } from "lucide-react";
import { AiSuggestionTag } from "~/custom-components/profile/edit/ai-suggestion-tag";
import { useAuthorization } from "~/hooks/use-authorization";
import { client, useMutate } from "../../../../types/api";

interface TopicsProps {
  profile: components["schemas"]["SearchProfileDetailResponse"];
  setProfile: (
    profile: components["schemas"]["SearchProfileDetailResponse"],
  ) => void;
}

export function Topics({ profile, setProfile }: TopicsProps) {
  const [selectedTopic, setSelectedTopic] = useState<string | undefined>(
    profile.topics.length > 0 ? profile.topics[0].name : undefined,
  );
  const [newTopicName, setNewTopicName] = useState("");
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
            <Button
              variant="destructive"
              onClick={() => {
                //TODO:
              }}
            >
              <Trash2 />
              {selectedTopic}
            </Button>
          )}
          <Input
            value={newTopicName}
            placeholder={"+ Add topic"}
            className={"w-[180px] shadow-none ml-auto"}
            onChange={(e) => setNewTopicName(e.target.value)}
            onKeyDown={(e) => {
              if (
                e.key === "Enter" &&
                !profile.topics.map((t) => t.name).includes(newTopicName)
              ) {
                //TODO:
              }
            }}
          />
        </div>

        {selectedTopic && <KeywordField keywords={selectedTopicKeywords} />}
        <div className={"pl-5 pr-5"}>
          <div className="flex gap-2 items-center pb-2">
            <Sparkles className={"w-4 h-4"} />
            <h2>AI Keyword Suggestions</h2>
          </div>

          <div className={"flex flex-wrap gap-2 pb-2"}>
            {selectedTopicKeywords.map((keyword) => (
              <AiSuggestionTag keyword={keyword} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
