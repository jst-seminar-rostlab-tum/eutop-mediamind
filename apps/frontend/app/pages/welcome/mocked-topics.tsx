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
import { toast } from "sonner";
import { useTranslation } from "react-i18next";
import type { Profile } from "types/model";
import { carKeywords, environmentKeywords } from "./mock-data";

interface TopicsProps {
  profile: Profile;
  setProfile: (profile: Profile) => void;
}

export function MockedTopics({ profile, setProfile }: TopicsProps) {
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

  const getSuggestions = (keywords: string[]) => {
    if (keywords.length === 0) {
      setAiSuggestions([]);
      return;
    }

    setIsLoadingSuggestions(true);

    setTimeout(() => {
      const lowerKeywords = keywords.map((k) => k.toLowerCase());
      const isEnvironment = lowerKeywords.some((k) =>
        ["co2", "renewable energy"].includes(k),
      );

      const sourceList = isEnvironment ? environmentKeywords : carKeywords;

      // Filter out already selected keywords
      const filtered = sourceList.filter(
        (suggestion) =>
          !keywords.some(
            (keyword) => keyword.toLowerCase() === suggestion.toLowerCase(),
          ),
      );

      // Shuffle
      const shuffled = [...filtered].sort(() => 0.5 - Math.random());

      // Ensure 3 items (pad if needed)
      const suggestions = shuffled.slice(0, 3);
      while (suggestions.length < 3 && shuffled.length < sourceList.length) {
        // Try to pad with other unique values from sourceList
        const extras = sourceList.filter(
          (kw) => !keywords.includes(kw) && !suggestions.includes(kw),
        );
        if (extras.length === 0) break;
        suggestions.push(extras[Math.floor(Math.random() * extras.length)]);
      }

      setAiSuggestions(suggestions.slice(0, 3));
      setIsLoadingSuggestions(false);
    }, 2000); // simulate delay
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
    toast.info(t("landing_page.add_topic"));
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
              {t("topics.delete_topic")}
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
                      {t("topics.no_suggestions")}
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
