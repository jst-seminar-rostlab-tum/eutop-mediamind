import { useEffect, useMemo, useState } from "react";
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
import { client } from "../../../../types/api";
import { useAuthorization } from "~/hooks/use-authorization";
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
  const [aiSuggestions, setAiSuggestions] = useState<string[]>([]);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);

  const selectedTopicKeywords = useMemo(() => {
    return (
      profile.topics.find((topic) => topic.name === selectedTopic)?.keywords ||
      []
    );
  }, [profile.topics, selectedTopic]);

  const { authorizationHeaders } = useAuthorization();

  const getSuggestions = async (keywords: string[]) => {
    if (keywords.length === 0) {
      setAiSuggestions([]);
      return;
    }

    setIsLoadingSuggestions(true);
    try {
      const result = await client.POST(
        "/api/v1/search-profiles/keywords/suggestions",
        {
          body: keywords,
        },
      );

      if (result.data?.suggestions) {
        const filteredSuggestions = result.data.suggestions.filter(
          (suggestion: string) =>
            !keywords.some(
              (keyword) => keyword.toLowerCase() === suggestion.toLowerCase(),
            ),
        );
        setAiSuggestions(filteredSuggestions);
      }
    } catch (error) {
      console.error("Failed to fetch AI suggestions:", error);
      toast.error("Failed to get AI suggestions.");
      setAiSuggestions([]);
    } finally {
      setIsLoadingSuggestions(false);
    }
  };

  useEffect(() => {
    if (selectedTopic && selectedTopicKeywords.length > 0) {
      getSuggestions(selectedTopicKeywords);
    } else {
      setAiSuggestions([]);
    }
  }, [selectedTopic, selectedTopicKeywords]);

  const handleAddSuggestionAsKeyword = (suggestion: string) => {
    if (selectedTopic && !selectedTopicKeywords.includes(suggestion)) {
      const updatedTopics = profile.topics.map((topic) => {
        if (topic.name === selectedTopic) {
          return { ...topic, keywords: [...topic.keywords, suggestion] };
        }
        return topic;
      });
      setProfile({ ...profile, topics: updatedTopics });
      setAiSuggestions((prev) => prev.filter((s) => s !== suggestion));
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
                setAiSuggestions([]);
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
                setProfile({
                  ...profile,
                  topics: [
                    ...profile.topics,
                    { id: "", name: newTopicName, keywords: [] },
                  ],
                });
                setSelectedTopic(newTopicName);
                setNewTopicName("");
              }
            }}
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
                {isLoadingSuggestions && (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                )}
              </div>

              <div className={"flex flex-wrap gap-2 pb-2"}>
                {aiSuggestions.map((suggestion) => (
                  <AiSuggestionTag
                    key={suggestion}
                    keyword={suggestion}
                    onAdd={handleAddSuggestionAsKeyword}
                  />
                ))}
                {aiSuggestions.length === 0 &&
                  selectedTopicKeywords.length > 0 &&
                  !isLoadingSuggestions && (
                    <Label className="text-gray-500 italic">
                      No new suggestions available
                    </Label>
                  )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
