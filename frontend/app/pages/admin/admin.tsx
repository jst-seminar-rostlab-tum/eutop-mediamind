import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { DataTableSubscriptions } from "~/custom-components/admin-settings/data-table-subs";
import Layout from "~/custom-components/layout";
import Text from "~/custom-components/text";
import React from "react";
import { getOrgaColumns, getSubsColumns } from "./columns";
import { OrganizationDialog } from "./dialogs/organization-dialog";
import { SubscriptionDialog } from "./dialogs/subscription-dialog";

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "~/components/ui/breadcrumb";
import { useTranslation } from "react-i18next";
import { ConfirmationDialog } from "~/custom-components/confirmation-dialog";
import { Building2, Newspaper } from "lucide-react";
import { DataTableOrganizations } from "~/custom-components/admin-settings/data-table-orgas";
import { Link } from "react-router";
import { client, useQuery } from "types/api";
import type { Organization, Subscription } from "../../../types/model";
import { toast } from "sonner";

const suppressSWRReloading = {
  refreshInterval: 0,
  refreshWhenHidden: false,
  revalidateOnFocus: false,
  refreshWhenOffline: false,
  revalidateIfStale: false,
  revalidateOnReconnect: false,
};

export function AdminPage() {
  //Organizations
  const [editedOrga, setEditedOrga] = React.useState<Organization | null>(null);
  const [showOrgaDialog, setShowOrgaDialog] = React.useState(false);
  const [isEditOrgaMode, setIsEditOrgaMode] = React.useState(false);

  // Subscriptions
  const [editedSub, setEditedSub] = React.useState<Subscription | null>(null);
  const [showSubsDialog, setShowSubsDialog] = React.useState(false);
  const [isEditSubsMode, setIsEditSubsMode] = React.useState(false);

  const [openDeleteDialog, setOpenDeleteDialog] = React.useState(false);
  const [deleteTarget, setDeleteTarget] = React.useState<{
    type: "organization" | "subscription";
    data: Organization | Subscription;
  } | null>(null);

  const { t } = useTranslation();

  const {
    data: organizations,
    // isLoading: orgasLoading,
    error: orgasError,
    mutate: mutateOrgas,
  } = useQuery("/api/v1/organizations", undefined, suppressSWRReloading);

  const {
    data: subscriptions,
    // isLoading: subsLoading,
    error: subsError,
    mutate: mutateSubs,
  } = useQuery("/api/v1/subscriptions", undefined, suppressSWRReloading);

  if (orgasError) {
    toast.success(t("admin.orgas_error"));
  }

  if (subsError) {
    toast.success(t("admin.subs_error"));
  }

  /*
  Organization Functions
  */

  async function handleDeleteOrganization(orga: Organization) {
    try {
      const result = await client.DELETE(
        "/api/v1/organizations/{organization_id}",
        {
          params: { path: { organization_id: orga.id } },
        },
      );
      if (result.error) {
        throw new Error(result.error as string);
      }
      await mutateOrgas();
      toast.success(t("organization-dialog.delete_success"));
    } catch (error) {
      console.error(error);
      toast.error(t("organization-dialog.delete_failed"));
    }
  }

  function handleEditOrganization(orga: Organization) {
    setEditedOrga(orga);
    setIsEditOrgaMode(true);
    setShowOrgaDialog(true);
  }

  const handleSaveOrganization = async (orga: Organization) => {
    try {
      const requestData = {
        name: orga.name,
        email: "test@email.com", // field maybe outdated
        user_ids: orga.users.map((user) => user.id ?? ""),
      };

      if (!isEditOrgaMode) {
        const result = await client.POST("/api/v1/organizations", {
          body: requestData,
        });
        if (result.error) {
          throw new Error(result.error as string);
        }
        await mutateOrgas();
        toast.success(t("organization-dialog.create_success"));
      } else {
        const result = await client.PUT(
          "/api/v1/organizations/{organization_id}",
          {
            params: { path: { organization_id: orga.id } },
            body: requestData,
          },
        );
        if (result.error) {
          throw new Error(result.error as string);
        }
        mutateOrgas();
        toast.success(t("organization-dialog.update_success"));
      }
    } catch (error) {
      console.error(error);
      toast.error(
        isEditOrgaMode
          ? t("organization-dialog.update_failed")
          : t("organization-dialog.create_failed"),
      );
    } finally {
      setShowOrgaDialog(false);
      setIsEditOrgaMode(false);
    }
  };

  /*
  Subscriptions Functions
  */

  async function handleSaveSubscription(data: {
    id: string;
    name: string;
    url: string;
    paywall: boolean;
    username: string;
    password: string;
  }) {
    try {
      const requestData = {
        name: data.name,
        domain: data.url,
        paywall: data.paywall,
        username: data.username,
        password: data.password,
      };
      if (!isEditSubsMode) {
        const result = await client.POST("/api/v1/subscriptions", {
          body: requestData,
        });
        if (result.error) {
          throw new Error(result.error as string);
        }
        mutateSubs();
        toast.success(t("subscription-dialog.create_success"));
      } else {
        const result = await client.PUT(
          "/api/v1/subscriptions/{subscription_id}",
          {
            params: { path: { subscription_id: data.id } },
            body: requestData,
          },
        );
        if (result.error) {
          throw new Error(result.error as string);
        }
        mutateSubs();
        toast.success(t("subscription-dialog.update_success"));
      }
    } catch (error) {
      console.error(error);
      toast.error(
        isEditSubsMode
          ? t("subscription-dialog.update_failed")
          : t("subscription-dialog.create_failed"),
      );
    } finally {
      setIsEditSubsMode(false);
      setShowSubsDialog(false);
    }
  }

  function handleEditSubscription(sub: Subscription) {
    setEditedSub(sub);
    setIsEditSubsMode(true);
    setShowSubsDialog(true);
  }

  async function handleDeleteSubscription(sub: Subscription) {
    try {
      const result = await client.DELETE(
        "/api/v1/subscriptions/{subscription_id}",
        {
          params: { path: { subscription_id: sub.id } },
        },
      );
      if (result.error) {
        throw new Error(result.error as string);
      }
      await mutateSubs();
      toast.success(t("subscription-dialog.delete_success"));
    } catch (error) {
      console.error(error);
      toast.error(t("subscription-dialog.delete_failed"));
    }
  }

  return (
    <>
      <Layout>
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink>
                <Link to="/dashboard">{t("breadcrumb_home")}</Link>
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>Admin-{t("admin.settings")}</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
        <Text hierachy={2}>{t("admin.header")}</Text>

        <div className="flex flex-col gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-xl flex">
                <Building2 className="mr-2" />
                {t("admin.orga_header")}
              </CardTitle>
              <CardDescription>{t("admin.orga_text")}</CardDescription>
            </CardHeader>
            <CardContent>
              <DataTableOrganizations
                columns={getOrgaColumns(
                  handleEditOrganization,
                  setDeleteTarget,
                  setOpenDeleteDialog,
                )}
                data={organizations ?? []}
                onAdd={() => {
                  setEditedOrga(null);
                  setIsEditOrgaMode(false);
                  setShowOrgaDialog(true);
                }}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-xl flex">
                <Newspaper className="mr-2" />
                {t("admin.subs_header")}
              </CardTitle>
              <CardDescription>{t("admin.subs_text")}</CardDescription>
            </CardHeader>
            <CardContent>
              <DataTableSubscriptions
                columns={getSubsColumns(
                  handleEditSubscription,
                  setDeleteTarget,
                  setOpenDeleteDialog,
                )}
                data={subscriptions ?? []}
                onAdd={() => {
                  setEditedSub(null);
                  setIsEditSubsMode(false);
                  setShowSubsDialog(true);
                }}
              />
            </CardContent>
          </Card>
        </div>

        <OrganizationDialog
          open={showOrgaDialog}
          onOpenChange={setShowOrgaDialog}
          isEdit={isEditOrgaMode}
          orga={editedOrga}
          onSave={handleSaveOrganization}
        />

        <SubscriptionDialog
          open={showSubsDialog}
          onOpenChange={setShowSubsDialog}
          isEdit={isEditSubsMode}
          sub={editedSub}
          onSave={handleSaveSubscription}
        />

        <ConfirmationDialog
          open={openDeleteDialog}
          onOpenChange={setOpenDeleteDialog}
          dialogType="delete"
          action={() => {
            if (deleteTarget) {
              if (deleteTarget.type === "organization") {
                const orga = deleteTarget.data as Organization;
                handleDeleteOrganization(orga);
              } else if (deleteTarget.type === "subscription") {
                const sub = deleteTarget.data as Subscription;
                handleDeleteSubscription(sub);
              }
            }
          }}
        />
      </Layout>
    </>
  );
}
