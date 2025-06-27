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
import {
  AlertCircleIcon,
  Eye,
  EyeOff,
  LogOut,
  OctagonAlert,
} from "lucide-react";
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
import { useTranslation } from "react-i18next";

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

  const { t } = useTranslation();

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
        <DialogContent className="min-w-[400px]">
          <DialogHeader>
            <DialogTitle>
              {isEdit
                ? t("subscription-dialog.edit_header")
                : t("subscription-dialog.add_header")}
            </DialogTitle>
            <DialogDescription>
              {isEdit
                ? t("subscription-dialog.edit_text")
                : t("subscription-dialog.add_text")}
            </DialogDescription>
          </DialogHeader>
          {showAlert && (
            <Alert className="mt-2" variant="destructive">
              <AlertCircleIcon />
              <AlertTitle>
                {t("subscription-dialog.credentials_error_header")}
              </AlertTitle>
              <AlertDescription>
                {t("subscription-dialog.credentials_error_text")}
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
            <Label className="text-right">
              {t("subscription-dialog.username")}
            </Label>
            <Input
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder={t("subscription-dialog.username")}
              className="col-span-3"
            />
          </div>

          <div className="grid grid-cols-4 items-center gap-4">
            <Label className="text-right">
              {t("subscription-dialog.password")}
            </Label>
            <Input
              type={visible ? "text" : "password"}
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={t("subscription-dialog.password")}
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
              {t("save_changes")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      <AlertDialog open={showLeaveConfirm} onOpenChange={setShowLeaveConfirm}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center">
              <OctagonAlert size={20} className="text-red-500 mr-2" />
              {t("confirmation-dialog.title")}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {t("confirmation-dialog.unsaved_text")}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{t("Cancel")}</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-white shadow-xs hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60"
              onClick={() => {
                setShowLeaveConfirm(false);
                onOpenChange(false); // close the main dialog
              }}
            >
              <LogOut className="text-white" />
              {t("Leave")}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
