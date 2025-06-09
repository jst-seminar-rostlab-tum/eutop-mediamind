import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Input } from "~/components/ui/input";
import { useState } from "react";
import { KeywordTag } from "~/custom-components/profile/edit/keyword-tag";
import type { Profile } from "../../../../types/model";

interface KeywordFieldProps {
  keywords: string[];
  setProfile: (profile: Profile) => void;
  profile: Profile;
  selectedTopic: string | undefined;
}

export function KeywordField({
  keywords,
  setProfile,
  profile,
  selectedTopic,
}: KeywordFieldProps) {
  const [newKeyword, setNewKeyword] = useState("");

  const handleAddKeyword = () => {
    if (newKeyword && selectedTopic && !keywords.includes(newKeyword)) {
      const updatedTopics = profile.topics.map((topic) => {
        if (topic.name === selectedTopic) {
          return { ...topic, keywords: [...topic.keywords, newKeyword] };
        }
        return topic;
      });
      setProfile({ ...profile, topics: updatedTopics });
      setNewKeyword("");
    }
  };

  const handleDeleteKeyword = (keywordToDelete: string) => {
    if (selectedTopic) {
      const updatedTopics = profile.topics.map((topic) => {
        if (topic.name === selectedTopic) {
          return {
            ...topic,
            keywords: topic.keywords.filter((k) => k !== keywordToDelete),
          };
        }
        return topic;
      });
      setProfile({ ...profile, topics: updatedTopics });
    }
  };

  return (
    <Card className="rounded-3xl shadow-none">
      <CardHeader>
        <CardTitle>Keywords</CardTitle>
      </CardHeader>
      <CardContent>
        <div className={"flex flex-wrap gap-2 pb-5"}>
          {keywords.map((keyword) => (
            <KeywordTag
              key={keyword}
              name={keyword}
              onDelete={handleDeleteKeyword}
            />
          ))}
          <Input
            value={newKeyword}
            onChange={(e) => setNewKeyword(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault(); // Prevent form submission
                handleAddKeyword();
              }
            }}
            placeholder={"+ Add keyword"}
            className={"w-[150px] border-0 shadow-none"}
          />
        </div>
      </CardContent>
    </Card>
  );
}
