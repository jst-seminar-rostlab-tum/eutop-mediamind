import type { JSX } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "~/components/ui/tabs";
import { DataTableMailing } from "~/custom-components/profile/edit/data-table-mailing";
import { Label } from "~/components/ui/label";
import type { Profile } from "../../../../types/model";
import { useTranslation } from "react-i18next";

export interface MailingProps {
  profile: Profile;
  setProfile: (profile: Profile) => void;
}

export function Mailing({ profile, setProfile }: MailingProps): JSX.Element {
  const { t } = useTranslation();

  const setInternalMails = (emails: string[]) =>
    setProfile({ ...profile, organization_emails: emails });

  const setExternalMails = (emails: string[]) =>
    setProfile({ ...profile, profile_emails: emails });

  return (
    <div className="overflow-hidden">
      <h2 className={"font-bold pt-3 pb-3"}>{t("mailing.header")}</h2>
      <Label className={"text-gray-400 font-normal pb-3"}>
        {t("mailing.info")}
      </Label>
      <Tabs className="overflow-hidden pt-3" defaultValue="internal">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="internal">{t("mailing.Internal")}</TabsTrigger>
          <TabsTrigger value="external">{t("mailing.External")}</TabsTrigger>
        </TabsList>
        <TabsContent className="overflow-hidden" value={"internal"}>
          <DataTableMailing
            name={t("mailing.Internal") + "e " + "Email"}
            dataArray={profile.organization_emails}
            setDataArray={setInternalMails}
          />
        </TabsContent>
        <TabsContent value={"external"}>
          <DataTableMailing
            name={t("mailing.External") + "e " + "Email"}
            dataArray={profile.profile_emails}
            setDataArray={setExternalMails}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
