import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "~/components/ui/tabs";
import { DataTable } from "~/custom-components/admin-settings/data-table";
import Layout from "~/custom-components/layout";
import Text from "~/custom-components/text";
import React from "react";
import type { Organization, Subscription, User } from "./types";
import { getOrgaColumns, getSubsColumns } from "./columns";
import { OrganizationDialog } from "./dialogs/organization-dialog";
import { SubscriptionDialog } from "./dialogs/subscription-dialog";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogFooter,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogCancel,
  AlertDialogAction,
} from "~/components/ui/alert-dialog";

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
  ];
}

export function AdminPage() {
  //Organizations
  const [orgaData, setOrgaData] = React.useState<Organization[]>([]);
  const [showOrgaDialog, setShowOrgaDialog] = React.useState(false);
  const [newOrgaName, setNewOrgaName] = React.useState("");
  const [initialOrgaName, setInitialOrgaName] = React.useState("");
  const [isEditOrgaMode, setIsEditOrgaMode] = React.useState(false);
  const [editingOrgIndex, setEditingOrgIndex] = React.useState<number | null>(
    null,
  );
  const [editingUserData, setEditingUserData] = React.useState<User[]>([]);
  const [searchInputForAdd, setSearchInputForAdd] = React.useState("");
  const [showOrgaNameAlert, setShowOrgaNameAlert] = React.useState(false);
  const [showAlert, setShowAlert] = React.useState(false);

  // Subscriptions
  const [subsData, setSubsData] = React.useState<Subscription[]>([]);
  const [initialSub, setInitialSub] = React.useState<Subscription>();
  const [showSubsDialog, setShowSubsDialog] = React.useState(false);
  const [newSubsName, setNewSubsName] = React.useState("");
  const [newURL, setNewURL] = React.useState("");
  const [newUsername, setNewUsername] = React.useState("");
  const [newPassword, setNewPassword] = React.useState("");
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
    // reset from possible previous dialog
    setShowAlert(false);
    setShowOrgaNameAlert(false);
    // set false on open for safety
    setUnsavedEdits(false);
    const index = orgaData.findIndex((org) => org.name === name);
    if (index !== -1) {
      setInitialOrgaName(orgaData[index].name); // to catch edge case if you edit back to initial name as no changes
      setNewOrgaName(orgaData[index].name);
      setEditingOrgIndex(index);
      setIsEditOrgaMode(true);

      // call api here to get the actual users of this org
      const usersForOrg = orgaData[index].users ?? [];
      setEditingUserData(usersForOrg);

      setShowOrgaDialog(true);
    }
  }

  function handleSaveOrganization() {
    if (!newOrgaName.trim()) {
      setShowOrgaNameAlert(true);
      return;
    }

    const trimmedName = newOrgaName.trim();

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

    setNewOrgaName("");
    setShowOrgaDialog(false);
    setIsEditOrgaMode(false);
    setEditingOrgIndex(null);
    setUnsavedEdits(false);
  }

  // Subscriptions Functions

  function handleSaveSubscription() {
    if (
      !newSubsName.trim() ||
      !newURL.trim() ||
      !newUsername.trim() ||
      !newPassword.trim()
    ) {
      setShowAlert(true);
      return;
    }
    setShowAlert(false);
    const newSubs = {
      name: newSubsName.trim(),
      url: newURL.trim(),
      username: newUsername.trim(),
      password: newPassword.trim(),
    };

    if (isEditSubsMode && editingSubsIndex !== null) {
      setSubsData((prev) =>
        prev.map((sub, i) => (i === editingSubsIndex ? newSubs : sub)),
      );
    } else {
      setSubsData((prev) => [...prev, newSubs]);
    }

    // reset
    setNewSubsName("");
    setNewURL("");
    setNewUsername("");
    setNewPassword("");
    setIsEditSubsMode(false);
    setEditingSubsIndex(null);
    setShowSubsDialog(false);

    setUnsavedEdits(false);
  }

  function handleEditSubscription(index: number) {
    const sub = subsData[index];
    setInitialSub(sub);

    setNewSubsName(sub.name);
    setNewURL(sub.url);
    setNewUsername(sub.username);
    setNewPassword(sub.password);
    setEditingSubsIndex(index);
    setIsEditSubsMode(true);
    setShowSubsDialog(true);
  }

  function handleDeleteSubscription(index: number) {
    setSubsData((prev) => prev.filter((_, i) => i !== index));
  }

  return (
    <>
      <Layout>
        <Text className="mt-10" hierachy={2}>
          Admin Settings
        </Text>
        <Tabs defaultValue="organizations" className="m-2">
          <TabsList className="w-full">
            <TabsTrigger value="organizations">Organizations</TabsTrigger>
            <TabsTrigger value="subscriptions">Subscriptions</TabsTrigger>
          </TabsList>

          <TabsContent value="organizations">
            <Card>
              <CardHeader>
                <CardTitle>Manage Organizations</CardTitle>
                <CardDescription>
                  Make changes to your Organizations here. You can add, edit or
                  delete them.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <DataTable
                  columns={getOrgaColumns(
                    handleEditOrganization,
                    setDeleteTarget,
                    setOpenDeleteDialog,
                  )}
                  data={orgaData}
                  onAdd={() => {
                    setIsEditOrgaMode(false);
                    setEditingOrgIndex(null);
                    setNewOrgaName("");
                    setEditingUserData([]);
                    setShowOrgaDialog(true);
                  }}
                />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="subscriptions">
            <Card>
              <CardHeader>
                <CardTitle>Manage Subscriptions</CardTitle>
                <CardDescription>
                  Make changes to your Subscriptions here. You can add, edit or
                  delete them.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <DataTable
                  columns={getSubsColumns(
                    handleEditSubscription,
                    setDeleteTarget,
                    setOpenDeleteDialog,
                  )}
                  data={subsData}
                  onAdd={() => {
                    setNewSubsName("");
                    setNewURL("");
                    setNewUsername("");
                    setNewPassword("");
                    setIsEditSubsMode(false);
                    setEditingSubsIndex(null);
                    setShowSubsDialog(true);
                  }}
                />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <OrganizationDialog
          open={showOrgaDialog}
          onOpenChange={setShowOrgaDialog}
          isEdit={isEditOrgaMode}
          name={newOrgaName}
          onNameChange={setNewOrgaName}
          users={editingUserData}
          setUsers={setEditingUserData}
          searchInput={searchInputForAdd}
          setSearchInput={setSearchInputForAdd}
          onSave={handleSaveOrganization}
          unsavedEdits={unsavedEdits}
          setUnsavedEdits={setUnsavedEdits}
          initialOrgaName={initialOrgaName}
          showAlert={showAlert}
          setShowAlert={setShowAlert}
          showOrgaNameAlert={showOrgaNameAlert}
        />

        <SubscriptionDialog
          open={showSubsDialog}
          onOpenChange={setShowSubsDialog}
          isEdit={isEditSubsMode}
          name={newSubsName}
          url={newURL}
          username={newUsername}
          password={newPassword}
          setName={setNewSubsName}
          setURL={setNewURL}
          setUsername={setNewUsername}
          setPassword={setNewPassword}
          onSave={handleSaveSubscription}
          showAlert={showAlert}
          initialSub={initialSub}
        />

        <AlertDialog open={openDeleteDialog} onOpenChange={setOpenDeleteDialog}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Are you sure?</AlertDialogTitle>
              <AlertDialogDescription>
                This will permanently delete this entity
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction
                className="bg-destructive text-white shadow-xs hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60"
                onClick={() => {
                  if (deleteTarget) {
                    if (deleteTarget.type === "organization") {
                      handleDeleteOrganization(
                        deleteTarget.identifier as string,
                      );
                    } else if (deleteTarget.type === "subscription") {
                      handleDeleteSubscription(
                        deleteTarget.identifier as number,
                      );
                    }
                  }

                  setOpenDeleteDialog(false);
                  setDeleteTarget(null); // clear after use
                }}
              >
                Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </Layout>
    </>
  );
}
