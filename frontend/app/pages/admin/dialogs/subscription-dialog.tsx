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
import { Button } from "~/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "~/components/ui/alert";
import React from "react";
import { AlertCircleIcon } from "lucide-react";

type Props = {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  isEdit: boolean;
  name: string;
  url: string;
  username: string;
  password: string;
  setName: (value: string) => void;
  setURL: (value: string) => void;
  setUsername: (value: string) => void;
  setPassword: (value: string) => void;
  onSave: () => void;
  showAlert: boolean;
};

export function SubscriptionDialog({
  open,
  onOpenChange,
  isEdit,
  name,
  url,
  username,
  password,
  setName,
  setURL,
  setUsername,
  setPassword,
  onSave,
  showAlert,
}: Props) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>
            {isEdit ? "Edit Subscription" : "Add Subscription"}
          </DialogTitle>
          <DialogDescription>
            {isEdit
              ? "Edit your subscription here. Click save when you're done."
              : "Enter the credentials of the subscription you want to add. Click save when you're done."}
          </DialogDescription>
        </DialogHeader>
        {showAlert && (
          <Alert className="mt-2" variant="destructive">
            <AlertCircleIcon />
            <AlertTitle>Invalid Credentials</AlertTitle>
            <AlertDescription>
              Please insert valid credentials.
            </AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-4 items-center gap-4">
          <Label className="text-right">Name</Label>
          <Input
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Name"
            className="col-span-3"
          />
        </div>

        <div className="grid grid-cols-4 items-center gap-4">
          <Label className="text-right">URL</Label>
          <Input
            id="url"
            value={url}
            onChange={(e) => setURL(e.target.value)}
            placeholder="URL"
            className="col-span-3"
          />
        </div>

        <div className="grid grid-cols-4 items-center gap-4">
          <Label className="text-right">Username</Label>
          <Input
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Username"
            className="col-span-3"
          />
        </div>

        <div className="grid grid-cols-4 items-center gap-4">
          <Label className="text-right">Password</Label>
          <Input
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            className="col-span-3"
          />
        </div>

        <DialogFooter>
          <Button type="submit" onClick={onSave}>
            Save changes
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
