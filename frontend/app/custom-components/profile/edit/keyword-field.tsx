import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { KeywordTag } from "~/custom-components/profile/edit/keyword-tag";
import { Input } from "~/components/ui/input";

interface KeywordFieldProps {
  keywords: string[];
}

export function KeywordField({ keywords }: KeywordFieldProps) {
  return (
    <Card className="rounded-3xl shadow-none">
      <CardHeader>
        <CardTitle>Keywords</CardTitle>
      </CardHeader>
      <CardContent>
        <div className={"flex flex-wrap gap-2 pb-2"}>
          {keywords.map((keyword) => (
            <KeywordTag name={keyword} />
          ))}
          <Input
            placeholder={"+ Add keyword"}
            className={"w-[150px] border-0 shadow-none"}
          />
        </div>
      </CardContent>
    </Card>
  );
}
