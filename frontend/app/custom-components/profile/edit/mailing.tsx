import type { Profile } from "~/types/profile";
import type { JSX } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "~/components/ui/tabs";
import { MailingTable } from "~/custom-components/profile/edit/mailing-table";

export interface MailingProps {
  profile: Profile;
}

export function Mailing({ profile }: MailingProps): JSX.Element {
  return (
    <div>
      <Tabs defaultValue="internal" >
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="internal">Internal</TabsTrigger>
          <TabsTrigger value="external">External</TabsTrigger>
        </TabsList>
        <TabsContent value={"internal"}>
          <MailingTable mails={profile.organization_emails}/>
        </TabsContent>
        <TabsContent value={"external"}>
          <MailingTable mails={profile.profile_emails}/>
        </TabsContent>
      </Tabs>
    </div>
  );
}

