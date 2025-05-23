import type { Subscription } from "~/types/profile";
import { DataTable } from "~/custom-components/profile/edit/data-table";

export interface SubscriptionsProps {
  subscriptions: Subscription[];
}

export function Subscriptions({ subscriptions }: SubscriptionsProps) {
  const subscriptionWebsites = subscriptions.map(
    (subscriptions) => subscriptions.name,
  );
  return (
    <div>
      <DataTable
        name={"Subscription"}
        dataArray={subscriptionWebsites}
      ></DataTable>
    </div>
  );
}
