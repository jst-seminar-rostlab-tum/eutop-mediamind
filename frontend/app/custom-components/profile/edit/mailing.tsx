import type { Profile } from "~/types/profile";
import type { JSX } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "~/components/ui/tabs";
import { DataTable } from "~/custom-components/profile/edit/data-table";
import { Switch } from "~/components/ui/switch";
import { Label } from "~/components/ui/label";
import { Separator } from "~/components/ui/separator";

export interface MailingProps {
  profile: Profile;
}

export function Mailing({ profile }: MailingProps): JSX.Element {
  return (
    <div>
      <h2 className={"font-bold pt-3 pb-3"}>Press Releases</h2>
      <div className={"flex items-center gap-3 pb-4"}>
        <Label className={"text-gray-400 font-normal"}>
          Distribute press releases
        </Label>
        <Switch />
      </div>
      <Separator />
      <h2 className={"font-bold pt-3 pb-3"}>Mailing List</h2>
      <Tabs defaultValue="internal">
        <Label className={"text-gray-400 font-normal pb-3"}>
          Configure profile contact database for press release distribution
        </Label>

        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="internal">Internal</TabsTrigger>
          <TabsTrigger value="external">External</TabsTrigger>
        </TabsList>
        <TabsContent value={"internal"}>
          <DataTable name={"Email"} dataArray={profile.organization_emails} />
        </TabsContent>
        <TabsContent value={"external"}>
          <DataTable name={"Email"} dataArray={profile.profile_emails} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
