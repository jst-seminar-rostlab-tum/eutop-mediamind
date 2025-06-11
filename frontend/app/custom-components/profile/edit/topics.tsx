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
import { Sparkles, Trash2 } from "lucide-react";
import { AiSuggestionTag } from "~/custom-components/profile/edit/ai-suggestion-tag";
import type { Profile } from "../../../../types/model";
import { toast } from "sonner";

interface TopicsProps {
  profile: Profile;
  setProfile: (profile: Profile) => void;
}

export function Topics({ profile, setProfile }: TopicsProps) {
  const [selectedTopic, setSelectedTopic] = useState<string | undefined>(
    profile.topics.length > 0 ? profile.topics[0].name : undefined,
  );
  const [newTopicName, setNewTopicName] = useState("");
  const selectedTopicKeywords =
    profile.topics.find((topic) => topic.name === selectedTopic)?.keywords ||
    [];

  const handleAddTopic = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key !== "Enter") return;

    if (!profile.topics.map((t) => t.name).includes(newTopicName)) {
      setProfile({
        ...profile,
        topics: [
          ...profile.topics,
          { id: "", name: newTopicName, keywords: [] },
        ],
      });
      setSelectedTopic(newTopicName);
      setNewTopicName("");
    } else {
      toast.error("Can't add the same topic twice");
    }
  };

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
                setProfile({
                  ...profile,
                  topics: profile.topics.filter(
                    (t) => t.name !== selectedTopic,
                  ),
                });
                setSelectedTopic(undefined);
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
            onKeyDown={handleAddTopic}
          />
        </div>

        {selectedTopic && (
          <>
            <KeywordField
              keywords={selectedTopicKeywords}
              setProfile={setProfile}
              profile={profile}
              selectedTopic={selectedTopic}
            />
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
          </>
        )}
      </div>
    </div>
  );
}
