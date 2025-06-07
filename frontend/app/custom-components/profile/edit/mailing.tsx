import type { JSX } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "~/components/ui/tabs";
import { DataTableMailing } from "~/custom-components/profile/edit/data-table-mailing";
import { Label } from "~/components/ui/label";
import type { components } from "../../../../types/api-types-v1";

export interface MailingProps {
  profile: components["schemas"]["SearchProfileDetailResponse"];
  setProfile: (profile: components["schemas"]["SearchProfileDetailResponse"]) => void;
}

export function Mailing({ profile, setProfile }: MailingProps): JSX.Element {
  const setInternalMails = (emails: string[]) =>
    setProfile({ ...profile, organization_emails: emails });
  const setExternalMails = (emails: string[]) =>
    setProfile({ ...profile, profile_emails: emails });

  return (
    <div>
      <h2 className={"font-bold pt-3 pb-3"}>Mailing List</h2>
      <Label className={"text-gray-400 font-normal pb-3"}>
        Configure profile contact database for press release distribution
      </Label>
      <Tabs defaultValue="internal" className={"pt-3"}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="internal">Internal</TabsTrigger>
          <TabsTrigger value="external">External</TabsTrigger>
        </TabsList>
        <TabsContent value={"internal"}>
          <DataTableMailing
            name={"Internal Email"}
            dataArray={profile.organization_emails}
            setDataArray={setInternalMails}
          />
        </TabsContent>
        <TabsContent value={"external"}>
          <DataTableMailing
            name={"External Email"}
            dataArray={profile.profile_emails}
            setDataArray={setExternalMails}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
