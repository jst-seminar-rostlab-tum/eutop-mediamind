import type { Subscription } from "~/types/profile";
import { Label } from "~/components/ui/label";
import { DataTableSubsciptions } from "~/custom-components/profile/edit/data-table-subscriptions";

export interface SubscriptionsProps {
  subscriptions: Subscription[];
}

export function Subscriptions({ subscriptions }: SubscriptionsProps) {
  const subscriptionWebsites = subscriptions.map(
    (subscriptions) => subscriptions.name,
  );
  return (
    <div>
      <h2 className={"font-bold pt-3 pb-3"}>Sources</h2>
      <Label className={"text-gray-400 font-normal pb-4"}>
        Configure web scraping sources used for the external mailing list.
      </Label>
      <DataTableSubsciptions
        name={"Source"}
        dataArray={subscriptionWebsites}
      ></DataTableSubsciptions>
    </div>
  );
}
