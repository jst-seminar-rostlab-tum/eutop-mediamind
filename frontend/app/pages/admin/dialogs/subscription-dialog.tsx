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
import React, { useState } from "react";
import { AlertCircleIcon, Eye, EyeOff } from "lucide-react";
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
import type { Subscription } from "../types";

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
  initialSub?: Subscription;
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
  initialSub,
}: Props) {
  const [visible, setVisible] = useState(false);
  const [showLeaveConfirm, setShowLeaveConfirm] = React.useState(false);

  return (
    <>
      <Dialog
        open={open}
        onOpenChange={(isOpen) => {
          let subChanged = false;
          if (initialSub) {
            subChanged =
              name !== initialSub.name ||
              url !== initialSub.url ||
              username !== initialSub.username ||
              password !== initialSub.password;
          }
          if (!isOpen && subChanged) {
            setShowLeaveConfirm(true); // show AlertDialog instead
          } else {
            onOpenChange(isOpen); // normal open/close
          }
        }}
      >
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
              type={visible ? "text" : "password"}
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              className="col-span-3"
            />
            <Button
              type="button"
              variant="ghostNoHover"
              size="icon"
              className="absolute right-6"
              onClick={() => setVisible((v) => !v)}
            >
              {visible ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </Button>
          </div>

          <DialogFooter>
            <Button type="submit" onClick={onSave}>
              Save changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      <AlertDialog open={showLeaveConfirm} onOpenChange={setShowLeaveConfirm}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              You have unsaved changes right now
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-white shadow-xs hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60"
              onClick={() => {
                setShowLeaveConfirm(false);
                onOpenChange(false); // close the main dialog
              }}
            >
              Leave
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
