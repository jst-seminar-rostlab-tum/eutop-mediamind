import type { Profile } from "~/types/profile";
import type { JSX } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "~/components/ui/tabs";
import { DataTable } from "~/custom-components/profile/edit/data-table";

export interface MailingProps {
  profile: Profile;
}

export function Mailing({ profile }: MailingProps): JSX.Element {
  return (
    <div>
      <Tabs defaultValue="internal">
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
