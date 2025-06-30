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
import type { Organization, Subscription, User } from "./types";
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

// Fetch Orgas
async function getOrgaData(): Promise<Organization[]> {
  // Fetch data from your API here
  return [
    {
      name: "BMW",
      users: [
        { name: "jonathan@bmw.com", role: "admin" },
        { name: "rafael@bmw.com", role: "user" },
        { name: "leo@bmw.com", role: "user" },
      ],
    },
    {
      name: "Allianz",
      users: [{ name: "leo@allianz.com", role: "user" }],
    },
    {
      name: "EUTOP",
      users: [{ name: "leo@eutop.com", role: "user" }],
    },
    {
      name: "ADAC",
      users: [{ name: "leo@adac.com", role: "user" }],
    },
    {
      name: "Audi",
      users: [{ name: "leo@adac.com", role: "user" }],
    },
    {
      name: "TUM",
      users: [{ name: "leo@adac.com", role: "user" }],
    },
    {
      name: "Mercedes",
      users: [{ name: "leo@adac.com", role: "user" }],
    },
    {
      name: "Dell",
      users: [{ name: "leo@adac.com", role: "user" }],
    },
    {
      name: "Facebook",
      users: [{ name: "leo@adac.com", role: "user" }],
    },
    {
      name: "Google",
      users: [{ name: "leo@adac.com", role: "user" }],
    },
  ];
}

//Fetch Subs
async function getSubsData(): Promise<Subscription[]> {
  // Fetch data from your API here
  return [
    {
      name: "Spiegel",
      url: "spiegel-online.de",
      username: "Test_123",
      password: "Spiegel_123",
    },
    {
      name: "SZ",
      url: "sz.de",
      username: "Test_456",
      password: "SZ_123",
    },
    {
      name: "Spiegel",
      url: "spiegel-online.de",
      username: "Test_123",
      password: "Spiegel_123",
    },
    {
      name: "SZ",
      url: "sz.de",
      username: "Test_456",
      password: "SZ_123",
    },
    {
      name: "Spiegel",
      url: "spiegel-online.de",
      username: "Test_123",
      password: "Spiegel_123",
    },
    {
      name: "SZ",
      url: "sz.de",
      username: "Test_456",
      password: "SZ_123",
    },
  ];
}

export function AdminPage() {
  //Organizations
  const [orgaData, setOrgaData] = React.useState<Organization[]>([]);
  const [showOrgaDialog, setShowOrgaDialog] = React.useState(false);
  const [initialOrgaName, setInitialOrgaName] = React.useState("");
  const [isEditOrgaMode, setIsEditOrgaMode] = React.useState(false);
  const [editingOrgIndex, setEditingOrgIndex] = React.useState<number | null>(
    null,
  );
  const [editingUserData, setEditingUserData] = React.useState<User[]>([]);

  // Subscriptions
  const [subsData, setSubsData] = React.useState<Subscription[]>([]);
  const [initialSub, setInitialSub] = React.useState<Subscription>();
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

  React.useEffect(() => {
    async function fetchData() {
      const data = await getOrgaData();
      setOrgaData(data);
    }
    fetchData();
  }, []);

  React.useEffect(() => {
    async function fetchData() {
      const data = await getSubsData();
      setSubsData(data);
    }
    fetchData();
  }, []);

  function handleDeleteOrganization(name: string) {
    setOrgaData((prev) => prev.filter((org) => org.name !== name));
  }

  function handleEditOrganization(name: string) {
    // set false on open for safety
    setUnsavedEdits(false);
    const index = orgaData.findIndex((org) => org.name === name);
    if (index !== -1) {
      setInitialOrgaName(orgaData[index].name); // to catch edge case if you edit back to initial name as no changes
      setEditingOrgIndex(index);
      setIsEditOrgaMode(true);

      // call api here to get the actual users of this org
      const usersForOrg = orgaData[index].users ?? [];
      setEditingUserData(usersForOrg);

      setShowOrgaDialog(true);
    }
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
        <Breadcrumb className="mt-8">
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink href="/dashboard">Home</BreadcrumbLink>
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
                data={orgaData}
                onAdd={() => {
                  setIsEditOrgaMode(false);
                  setEditingOrgIndex(null);
                  setEditingUserData([]);
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
                data={subsData}
                onAdd={() => {
                  setIsEditSubsMode(false);
                  setEditingSubsIndex(null);
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
          users={editingUserData}
          setUsers={setEditingUserData}
          onSave={handleSaveOrganization}
          unsavedEdits={unsavedEdits}
          setUnsavedEdits={setUnsavedEdits}
          initialOrgaName={initialOrgaName}
        />

        <SubscriptionDialog
          open={showSubsDialog}
          onOpenChange={setShowSubsDialog}
          isEdit={isEditSubsMode}
          onSave={handleSaveSubscription}
          initialSub={initialSub}
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
