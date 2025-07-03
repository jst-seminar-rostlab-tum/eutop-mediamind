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
import React, { useEffect } from "react";
import type { User } from "./types";
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
import { useQuery } from "types/api";
import type { Organization, Subscription } from "../../../types/model";

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
  const [orgaData, setOrgaData] = React.useState<Organization[]>([]);
  const [editedOrga, setEditedOrga] = React.useState<Organization>();
  const [showOrgaDialog, setShowOrgaDialog] = React.useState(false);
  const [isEditOrgaMode, setIsEditOrgaMode] = React.useState(false);
  const [editingOrgIndex, setEditingOrgIndex] = React.useState<number | null>(
    null,
  );
  const [editedUserData, setEditedUserData] = React.useState<User[]>([]);

  // Subscriptions
  const [subsData, setSubsData] = React.useState<Subscription[]>([]);
  //const [editedSub, setEditedSub] = React.useState<Subscription>();
  const [showSubsDialog, setShowSubsDialog] = React.useState(false);
  const [isEditSubsMode, setIsEditSubsMode] = React.useState(false);
  const [editingSubsIndex, setEditingSubsIndex] = React.useState<number | null>(
    null,
  );

  const [unsavedEdits, setUnsavedEdits] = React.useState(false);
  const [openDeleteDialog, setOpenDeleteDialog] = React.useState(false);
  const [deleteTarget, setDeleteTarget] = React.useState<{
    type: "organization" | "subscription";
    identifier: string | number; // name for org, index for sub
  } | null>(null);


  const {
    data: organizations,
    // isLoading: orgasLoading,
    // error : orgasError,
    // mutate : mutateOrgas,
  } = useQuery("/api/v1/organizations", undefined, suppressSWRReloading);

      const {
    data: subscriptions,
    // isLoading: subsLoading,
    // error: subsError,
    // mutate: mutateSubs,
  } = useQuery("/api/v1/subscriptions", undefined, suppressSWRReloading);



  // Organization Functions

  function handleDeleteOrganization(name: string) {
    setOrgaData((prev) => prev.filter((org) => org.name !== name));
  }

  function handleEditOrganization(orga: Organization, index: number) {

      setEditedOrga(orga);
      setEditingOrgIndex(index);
      setIsEditOrgaMode(true);
}

      setEditedUserData(usersForOrg);

      setShowOrgaDialog(true);
    
  }

  function handleSaveOrganization(data: { name: string }) {
    const trimmedName = data.name.trim();

    if (!trimmedName) {
      return;
    }

    if (isEditOrgaMode && editingOrgIndex !== null) {
      setOrgaData((prev) =>
        prev.map((org, i) =>
          i === editingOrgIndex
            ? { ...org, name: trimmedName, users: editingUserData }
            : org,
        ),
      );
    } else {
      setOrgaData((prev) => [
        ...prev,
        { name: trimmedName, users: editingUserData },
      ]);
    }

    setShowOrgaDialog(false);
    setIsEditOrgaMode(false);
    setEditingOrgIndex(null);
    setUnsavedEdits(false);
  }

  // Subscriptions Functions

  function handleSaveSubscription(data: {
    name: string;
    url: string;
    username: string;
    password: string;
  }) {
    if (
      !data.name.trim() ||
      !data.url.trim() ||
      !data.username.trim() ||
      !data.password.trim()
    ) {
      return;
    }
    const newSubs = {
      name: data.name.trim(),
      url: data.url.trim(),
      username: data.username.trim(),
      password: data.password.trim(),
    };

    if (isEditSubsMode && editingSubsIndex !== null) {
      setSubsData((prev) =>
        prev.map((sub, i) => (i === editingSubsIndex ? newSubs : sub)),
      );
    } else {
      setSubsData((prev) => [...prev, newSubs]);
    }
    setIsEditSubsMode(false);
    setEditingSubsIndex(null);
    setShowSubsDialog(false);

    setUnsavedEdits(false);
  }

  function handleEditSubscription(index: number) {
    const sub = subsData[index];
    setInitialSub(sub);

    setEditingSubsIndex(index);
    setIsEditSubsMode(true);
    setShowSubsDialog(true);
  }

  function handleDeleteSubscription(index: number) {
    setSubsData((prev) => prev.filter((_, i) => i !== index));
  }

  const { t } = useTranslation();

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
                  setIsEditSubsMode(false);
                  setEditingSubsIndex(null); // check if needed
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
          sub={editedSubscription}
          onSave={handleSaveSubscription}
        />

        <ConfirmationDialog
          open={openDeleteDialog}
          onOpenChange={setOpenDeleteDialog}
          dialogType="delete"
          action={() => {
            if (deleteTarget) {
              if (deleteTarget.type === "organization") {
                handleDeleteOrganization(deleteTarget.identifier as string);
              } else if (deleteTarget.type === "subscription") {
                handleDeleteSubscription(deleteTarget.identifier as number);
              }
            }
          }}
        />
      </Layout>
    </>
  );
}
