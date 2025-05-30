import type { ColumnDef } from "@tanstack/react-table";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "~/components/ui/tabs";
import { DataTable } from "~/custom-components/dataTable";
import Header from "~/custom-components/header";
import Layout from "~/custom-components/layout";
import Text from "~/custom-components/text";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "~/components/ui/dropdown-menu";
import { Button } from "~/components/ui/button";
import { MoreHorizontal, Trash } from "lucide-react";
import React from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "~/components/ui/dialog";
import { Label } from "@radix-ui/react-dropdown-menu";
import { Input } from "~/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import {
  AlertDialog,
  AlertDialogTrigger,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogFooter,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogCancel,
  AlertDialogAction,
} from "~/components/ui/alert-dialog";

export type Organization = {
  name: string;
  users: User[];
};

export type Subscription = {
  name: string;
  url: string;
  username: string;
  password: string;
};

export type User = {
  name: string;
  role: "admin" | "user";
};

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

export function getSubsColumns(
  onEdit: (index: number) => void,
  onDelete: (index: number) => void,
): ColumnDef<Subscription>[] {
  return [
    { accessorKey: "name", header: "Subscriptions" },
    { accessorKey: "url", header: "URL" },
    {
      id: "actions",
      cell: ({ row }) => {
        const index = row.index;
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <span className="sr-only">Open menu</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onEdit(index)}>
                Edit Subscription
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => onDelete(index)}
                className="text-red-500"
              >
                Delete Subscription
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ];
}

export function getUserColumns(
  onRoleChange: (index: number, role: "admin" | "user") => void,
  onDelete: (index: number) => void,
): ColumnDef<User>[] {
  return [
    {
      accessorKey: "name",
      header: "User",
    },
    {
      accessorKey: "role",
      header: "Role",
      cell: ({ row }) => {
        const role = row.getValue("role") as "admin" | "user";
        const index = row.index;

        return (
          <Select
            value={role}
            onValueChange={(newRole) =>
              onRoleChange(index, newRole as "admin" | "user")
            }
          >
            <SelectTrigger className="w-[120px]">
              <SelectValue placeholder="Select role" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="admin">admin</SelectItem>
              <SelectItem value="user">user</SelectItem>
            </SelectContent>
          </Select>
        );
      },
    },
    {
      id: "actions",
      cell: ({ row }) => {
        const index = row.index;
        return (
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant={"ghost"}>
                <Trash className="text-red-500" />
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                <AlertDialogDescription>
                  This will permanently remove the user from this organization.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={() => onDelete(index)}>
                  Delete
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        );
      },
    },
  ];
}
export function Admin() {
  //Organizations
  const [orgaData, setOrgaData] = React.useState<Organization[]>([]);
  const [showOrgaDialog, setShowOrgaDialog] = React.useState(false);
  const [newOrgaName, setNewOrgaName] = React.useState("");
  const [isEditMode, setIsEditMode] = React.useState(false);
  const [editingOrgIndex, setEditingOrgIndex] = React.useState<number | null>(
    null,
  );
  const [editingUserData, setEditingUserData] = React.useState<User[]>([]);
  const [searchInputForAdd, setSearchInputForAdd] = React.useState("");

  // Subscriptions
  const [subsData, setSubsData] = React.useState<Subscription[]>([]);
  const [showSubsDialog, setShowSubsDialog] = React.useState(false);
  const [newSubsName, setNewSubsName] = React.useState("");
  const [newURL, setNewURL] = React.useState("");
  const [newUsername, setNewUsername] = React.useState("");
  const [newPassword, setNewPassword] = React.useState("");
  const [isEditSubsMode, setIsEditSubsMode] = React.useState(false);
  const [editingSubsIndex, setEditingSubsIndex] = React.useState<number | null>(
    null,
  );

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

  const OrgaColumns: ColumnDef<Organization>[] = [
    {
      accessorKey: "name",
      header: "Organization Name",
    },
    {
      id: "actions",
      cell: ({ row }) => {
        const orgName = row.getValue("name") as string;
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <span className="sr-only">Open menu</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => handleEditOrganization(orgName)}>
                Edit Organization
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => handleDeleteOrganization(orgName)}
                className="text-red-500"
              >
                Delete Organization
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ];

  function handleDeleteOrganization(name: string) {
    setOrgaData((prev) => prev.filter((org) => org.name !== name));
  }

  function handleEditOrganization(name: string) {
    const index = orgaData.findIndex((org) => org.name === name);
    if (index !== -1) {
      setNewOrgaName(orgaData[index].name);
      setEditingOrgIndex(index);
      setIsEditMode(true);

      // call api here to get the actual users of this org
      const usersForOrg = orgaData[index].users ?? [];
      setEditingUserData(usersForOrg);

      setShowOrgaDialog(true);
    }
  }

  function handleAddNewUser() {
    const email = searchInputForAdd.trim().toLowerCase();
    // if mail is not blank and not already in list
    if (!email || editingUserData.some((u) => u.name.toLowerCase() === email))
      return;
    // add user
    setEditingUserData((prev) => [...prev, { name: email, role: "user" }]);
    setSearchInputForAdd("");
  }

  function handleSaveOrganization() {
    if (!newOrgaName.trim()) return;

    const trimmedName = newOrgaName.trim();

    if (isEditMode && editingOrgIndex !== null) {
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
    setIsEditMode(false);
    setEditingOrgIndex(null);
  }

  // Subscriptions Functions

  function handleSaveSubscription() {
    if (
      !newSubsName.trim() ||
      !newURL.trim() ||
      !newUsername.trim() ||
      !newPassword.trim()
    )
      return;

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
  }

  function handleEditSubscription(index: number) {
    const sub = subsData[index];
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
      <Header />
      <Layout>
        <Text className="mt-6" hierachy={1}>
          Admin Settings
        </Text>
        <Tabs className="m-4">
          <TabsList defaultValue="organizations" className="w-full">
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
                  columns={OrgaColumns}
                  data={orgaData}
                  onAdd={() => {
                    setIsEditMode(false);
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
                    handleDeleteSubscription,
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

        <Dialog open={showOrgaDialog} onOpenChange={setShowOrgaDialog}>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              {isEditMode && (
                <>
                  <DialogTitle>Edit Organization</DialogTitle>
                  <DialogDescription>
                    Edit your organization here. Click save when you're done.
                  </DialogDescription>
                </>
              )}
              {!isEditMode && (
                <>
                  <DialogTitle>Add Organization</DialogTitle>
                  <DialogDescription>
                    Enter the name of the organization you want to add. Click
                    save when you're done.
                  </DialogDescription>
                </>
              )}
            </DialogHeader>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label className="text-right">Name</Label>
              <Input
                id="name"
                value={newOrgaName}
                onChange={(e) => setNewOrgaName(e.target.value)}
                placeholder="New Organization"
                className="col-span-3"
              />
            </div>
            <div className="mt-4">
              <DataTable
                columns={getUserColumns(
                  (index, newRole) => {
                    // call back to update roles
                    setEditingUserData((prev) =>
                      prev.map((user, i) =>
                        i === index ? { ...user, role: newRole } : user,
                      ),
                    );
                  },
                  (index) => {
                    // handle delete
                    setEditingUserData((prev) =>
                      prev.filter((_, i) => i !== index),
                    );
                  },
                )}
                data={editingUserData}
                onSearchChange={setSearchInputForAdd}
                onAdd={() => {
                  handleAddNewUser();
                }}
              />
            </div>
            <DialogFooter>
              <Button type="submit" onClick={handleSaveOrganization}>
                Save changes
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        <Dialog open={showSubsDialog} onOpenChange={setShowSubsDialog}>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              {!isEditSubsMode && (
                <>
                  <DialogTitle>Add Subscription</DialogTitle>
                  <DialogDescription>
                    Enter the credentials of the subscription you want to add.
                    Click save when you're done.
                  </DialogDescription>
                </>
              )}
              {isEditSubsMode && (
                <>
                  <DialogTitle>Edit Subscription</DialogTitle>
                  <DialogDescription>
                    Edit your subscription here. Click save when you're done.
                  </DialogDescription>
                </>
              )}
            </DialogHeader>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label className="text-right">Name</Label>
              <Input
                id="name"
                value={newSubsName}
                onChange={(e) => setNewSubsName(e.target.value)}
                placeholder="Name"
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label className="text-right">URL</Label>
              <Input
                id="url"
                value={newURL}
                onChange={(e) => setNewURL(e.target.value)}
                placeholder="URL"
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label className="text-right">Username</Label>
              <Input
                id="username"
                value={newUsername}
                onChange={(e) => setNewUsername(e.target.value)}
                placeholder="Username"
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label className="text-right">Password</Label>
              <Input
                id="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Password"
                className="col-span-3"
              />
            </div>
            <DialogFooter>
              <Button type="submit" onClick={handleSaveSubscription}>
                Save changes
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </Layout>
    </>
  );
}
