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
import { MoreHorizontal } from "lucide-react";
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

export type Organization = {
  name: string;
};

export type Subscription = {
  name: string;
  url: string;
  username: string;
  password: string;
};

async function getOrgaData(): Promise<Organization[]> {
  // Fetch data from your API here
  return [
    {
      name: "BMW",
    },
    {
      name: "Allianz",
    },
    {
      name: "EUTOP",
    },
    {
      name: "ADAC",
    },
  ];
}

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

export const OrgaColumns: ColumnDef<Organization>[] = [
  {
    accessorKey: "name",
    header: "Organization Name",
  },
  {
    id: "actions",
    cell: () => {
      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">Open menu</span>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>Edit Organization</DropdownMenuItem>
            <DropdownMenuItem>Delete Organization</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];

export const SubsColumns: ColumnDef<Subscription>[] = [
  {
    accessorKey: "name",
    header: "Subscriptions",
  },
  {
    accessorKey: "url",
    header: "URL",
  },
  {
    id: "actions",
    cell: () => {
      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">Open menu</span>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>Edit Organization</DropdownMenuItem>
            <DropdownMenuItem>Delete Organization</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];

export function Admin() {
  const [orgaData, setOrgaData] = React.useState<Organization[]>([]);
  const [showOrgaDialog, setShowOrgaDialog] = React.useState(false);
  const [newOrgaName, setNewOrgaName] = React.useState("");

  const [subsData, setSubsData] = React.useState<Subscription[]>([]);
  const [showSubsDialog, setShowSubsDialog] = React.useState(false);
  const [newSubsName, setNewSubsName] = React.useState("");
  const [newURL, setNewURL] = React.useState("");
  const [newUsername, setNewUsername] = React.useState("");
  const [newPassword, setNewPassword] = React.useState("");

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

  function handleSaveOrganization() {
    if (!newOrgaName.trim()) return;

    const newOrga = { name: newOrgaName.trim() };
    setOrgaData((prev) => [...prev, newOrga]);
    setNewOrgaName(""); // reset field
    setShowOrgaDialog(false); // close dialog
  }

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

    setSubsData((prev) => [...prev, newSubs]);
    setNewSubsName(""); // reset field
    setNewURL(""); // reset field
    setNewUsername(""); // reset field
    setNewPassword(""); // reset field
    setShowSubsDialog(false); // close dialog
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
                  onAdd={() => setShowOrgaDialog(true)}
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
                  columns={SubsColumns}
                  data={subsData}
                  onAdd={() => setShowSubsDialog(true)}
                />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <Dialog open={showOrgaDialog} onOpenChange={setShowOrgaDialog}>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Add Organization</DialogTitle>
              <DialogDescription>
                Enter the name of the organization you want to add. Click save
                when you're done.
              </DialogDescription>
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
              <DialogTitle>Add Subscription</DialogTitle>
              <DialogDescription>
                Enter the name and address of the subscription you want to add.
                Click save when you're done.
              </DialogDescription>
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
