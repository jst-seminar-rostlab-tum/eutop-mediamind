import { isEqual } from "lodash-es";
import { Link2, Loader2, Newspaper } from "lucide-react";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import { client, useQuery } from "types/api";
import type { Subscription } from "types/model";
import { Button } from "~/components/ui/button";
import { Card } from "~/components/ui/card";
import { Label } from "~/components/ui/label";
import { Switch } from "~/components/ui/switch";
import { DataTableSubscriptions } from "~/custom-components/profile/edit/data-table-subscriptions";

export const OrganisationSettingsPage = ({
  organisationId,
}: {
  organisationId: string;
}) => {
  const { t } = useTranslation();
  const { data, isLoading, error, mutate } = useQuery(
    "/api/v1/organizations/{organization_id}",
    {
      params: { path: { organization_id: organisationId } },
    },
  );
  const [editedSubscriptions, setEditedSubscriptions] = useState<
    Subscription[]
  >(data?.subscriptions || []);
  const [editedPdfAsLink, setEditedPdfAsLink] = useState<boolean>(
    data?.pdf_as_link ?? false,
  );
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    setEditedSubscriptions(data?.subscriptions || []);
    setEditedPdfAsLink(!!data?.pdf_as_link);
  }, [data]);

  useEffect(() => {
    if (error) toast.error(t("organisation_settings.error"));
  }, [error]);

  const handleChangedSubscriptions = async (subscriptions: Subscription[]) => {
    setIsSaving(true);
    try {
      if (!isEqual(subscriptions, data?.subscriptions)) {
        const result = await client.PUT(
          `/api/v1/organizations/{organization_id}/subscriptions`,
          {
            params: {
              path: { organization_id: organisationId },
            },
            body: {
              organization_id: organisationId,
              subscriptions: subscriptions,
            },
          },
        );
        mutate({
          ...data!,
          subscriptions: result.data ?? [],
        });
      }
      if (!!data?.pdf_as_link !== !!editedPdfAsLink) {
        await client.PUT(`/api/v1/organizations/{organization_id}`, {
          params: { path: { organization_id: organisationId } },
          body: {
            ...data!,
            pdf_as_link: editedPdfAsLink,
            users: (data?.users ?? []).map((u) => ({
              id: u.id!,
              role: u.role,
            })),
          },
        });
        mutate({
          ...data!,
          pdf_as_link: editedPdfAsLink,
        });
      }
      toast.success(t("organisation_settings.success"));
    } catch {
      toast.error(t("organisation_settings.error"));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <>
      <Card className="px-6 py-0 pb-2 mb-4 gap-4 overflow-hidden">
        <div className="mt-4 flex flex-col overflow-hidden">
          <Label className="text-lg font-semibold mt-2">
            <Link2 className="mr-2" />
            {t("organisation_settings.pdf_as_link")}
          </Label>
          <div className="flex gap-2 mt-2">
            <Switch
              checked={editedPdfAsLink}
              onCheckedChange={setEditedPdfAsLink}
            />
            <Label className="text-sm text-muted-foreground mb-4">
              {t("organisation_settings.pdf_as_link_text")}
            </Label>
          </div>
          <Label className="text-lg font-semibold mt-2">
            <Newspaper className="mr-2" />
            {t("organisation_settings.subscriptions")}
          </Label>
          <p className="text-sm text-muted-foreground mb-4 mt-2">
            {t("organisation_settings.subscriptions_text")}
          </p>
          <DataTableSubscriptions
            name="Source"
            allSubscriptions={data?.subscriptions ?? []}
            setSubscriptions={setEditedSubscriptions}
            isLoading={isLoading}
          />
        </div>
        <div className="flex justify-end">
          <Button
            variant="default"
            size="sm"
            onClick={() => handleChangedSubscriptions(editedSubscriptions)}
            disabled={
              isSaving ||
              (isEqual(editedSubscriptions, data?.subscriptions) &&
                data?.pdf_as_link === editedPdfAsLink)
            }
            className="my-4 w-fit"
          >
            {isSaving && <Loader2 className="animate-spin mr-2 h-4 w-4" />}
            {t("Save")}
          </Button>
        </div>
      </Card>
    </>
  );
};
