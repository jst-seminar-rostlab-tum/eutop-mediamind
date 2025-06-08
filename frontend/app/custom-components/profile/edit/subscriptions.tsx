import { Label } from "~/components/ui/label";
import { DataTableSubscriptions } from "~/custom-components/profile/edit/data-table-subscriptions";
import type { Profile, Subscription } from "../../../../types/model";

export interface SubscriptionsProps {
  profile: Profile;
  setProfile: (profile: Profile) => void;
}

export function Subscriptions({ profile, setProfile }: SubscriptionsProps) {
  const setSubscriptions = (subscriptions: Subscription[]) =>
    setProfile({ ...profile, subscriptions: subscriptions });

  return (
    <div>
      <h2 className={"font-bold pt-3 pb-3"}>Sources</h2>
      <Label className={"text-gray-400 font-normal pb-4"}>
        Configure web scraping sources used for the external mailing list.
      </Label>
      <DataTableSubscriptions
        name={"Source"}
        allSubscriptions={profile.subscriptions}
        setSubscriptions={setSubscriptions}
      ></DataTableSubscriptions>
    </div>
  );
}
