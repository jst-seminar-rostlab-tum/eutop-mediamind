import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { KeywordTag } from "~/custom-components/profile/edit/keyword-tag";

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
        <div className={"flex flex-wrap gap-2"}>
          {keywords.map((keyword) => (
            <KeywordTag name={keyword} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
