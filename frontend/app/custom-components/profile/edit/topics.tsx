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
import { RefreshCcw, Sparkles, Trash2 } from "lucide-react";
import { AiSuggestionTag } from "~/custom-components/profile/edit/ai-suggestion-tag";
import type { Profile } from "../../../../types/model";
import { client } from "../../../../types/api";
import { toast } from "sonner";
import { useTranslation } from "react-i18next";

interface TopicsProps {
  profile: Profile;
  setProfile: (profile: Profile) => void;
}

export function Topics({ profile, setProfile }: TopicsProps) {
  const { t } = useTranslation();

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
          params: {
            query: {
              search_profile_name: profile.name,
              search_profile_language: profile.language, // Todo set to profile language once added in backend
            },
          },
          body: {
            selected_topic: { topic_name: selectedTopic ?? "", keywords },
            related_topics: profile.topics.map((t) => ({
              keywords: t.keywords,
              topic_name: t.name,
            })),
          },
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
      toast.error(t("topics.AI_error"));
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
      toast.error(t("topics.topic_error"));
    }
  };

  return (
    <div>
      <h2 className={"font-bold pt-3 pb-3"}>{t("topics.header")}</h2>
      <Label className={"text-gray-400 font-normal pb-4"}>
        {t("topics.info")}
      </Label>
      <div className="space-y-4">
        <div className={"flex gap-3"}>
          <Label>{t("topics.label")}</Label>
          <Select
            value={selectedTopic}
            onValueChange={(value) => setSelectedTopic(value)}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder={t("topics.select_topic")} />
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
            placeholder={t("topics.add")}
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
                <h2>{t("topics.AI_header")}</h2>
                {aiSuggestions.length > 0 && (
                  <Button
                    variant={"secondary"}
                    className={"h-8 w-8"}
                    onClick={() => {
                      getSuggestions(selectedTopicKeywords);
                    }}
                    disabled={isLoadingSuggestions}
                  >
                    <RefreshCcw />
                  </Button>
                )}
                {isLoadingSuggestions && (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                )}
              </div>
              {aiSuggestions.length === 0 && (
                <p className={"text-gray-400 text-sm"}>
                  {t("edit_profile.suggestions_text")}
                </p>
              )}
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
                      {t("topcs.no_suggestions")}
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
