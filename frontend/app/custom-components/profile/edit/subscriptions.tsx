import type { Profile, Subscription } from "~/types/profile";
import { Label } from "~/components/ui/label";
import { DataTableSubsciptions } from "~/custom-components/profile/edit/data-table-subscriptions";

export interface SubscriptionsProps {
  subscriptions: Subscription[];
  profile: Profile;
  setProfile: (profile: Profile) => void;
}

export function Subscriptions({
  subscriptions,
  profile,
  setProfile,
}: SubscriptionsProps) {
  const setSubscriptions = (subscriptions: Subscription[]) =>
    setProfile({ ...profile, subscriptions: subscriptions });

  return (
    <div>
      <h2 className={"font-bold pt-3 pb-3"}>Sources</h2>
      <Label className={"text-gray-400 font-normal pb-4"}>
        Configure web scraping sources used for the external mailing list.
      </Label>
      <DataTableSubsciptions
        name={"Source"}
        allSubscriptions={subscriptions}
        selectedSubscriptions={profile.subscriptions}
        setSubscriptions={setSubscriptions}
      ></DataTableSubsciptions>
    </div>
  );
}
