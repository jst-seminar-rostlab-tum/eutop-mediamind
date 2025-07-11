import { Label } from "~/components/ui/label";
import { DataTableSubscriptions } from "~/custom-components/profile/edit/data-table-subscriptions";
import type { Profile, Subscription } from "../../../../types/model";
import { useQuery } from "types/api";
import { useTranslation } from "react-i18next";

export interface SubscriptionsProps {
  profile: Profile;
  setProfile: (profile: Profile) => void;
}

export function Subscriptions({ profile, setProfile }: SubscriptionsProps) {
  const { data: availableSubscriptions } = useQuery("/api/v1/subscriptions");

  const setSubscriptions = (subscriptions: Subscription[]) =>
    setProfile({ ...profile, subscriptions: subscriptions });

  const profileSubscriptions = availableSubscriptions?.map((availableSub) => {
    return {
      ...availableSub,
      is_subscribed: profile.subscriptions.some(
        (sub) => sub.name === availableSub.name && sub.is_subscribed,
      ),
    };
  });

  const { t } = useTranslation();

  return (
    <div>
      <h2 className={"font-bold pt-3 pb-3"}>{t("subscriptions.header")}</h2>
      <Label className={"text-gray-400 font-normal pb-4"}>
        {t("subscriptions.info")}
      </Label>
      <DataTableSubscriptions
        name={t("subscriptions.source")}
        allSubscriptions={profileSubscriptions || []}
        setSubscriptions={setSubscriptions}
      ></DataTableSubscriptions>
    </div>
  );
}
