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
import React, { useState } from "react";
import { Eye, EyeOff } from "lucide-react";

import type { Subscription } from "../types";
import { useTranslation } from "react-i18next";
import { ConfirmationDialog } from "~/custom-components/confirmation-dialog";
import { cn } from "~/lib/utils";

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

          <div className="grid grid-cols-4 items-center gap-4">
            <Label className="text-right">Name</Label>
            <div className="flex items-center col-span-3">
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Name"
                className={cn(
                  "w-full pr-10",
                  name == "" &&
                    open &&
                    "border-2 border-destructive focus-visible:ring-destructive focus-visible:border-destructive",
                )}
              />
            </div>
          </div>

          <div className="grid grid-cols-4 items-center gap-4">
            <Label className="text-right">URL</Label>
            <div className="flex items-center col-span-3">
              <Input
                id="url"
                value={url}
                onChange={(e) => setURL(e.target.value)}
                placeholder="URL"
                className={cn(
                  "w-full pr-10",
                  url == "" &&
                    open &&
                    "border-2 border-destructive focus-visible:ring-destructive focus-visible:border-destructive",
                )}
              />
            </div>
          </div>

          <div className="grid grid-cols-4 items-center gap-4">
            <Label className="text-right">
              {t("subscription-dialog.username")}
            </Label>
            <div className="flex items-center col-span-3">
              <Input
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder={t("subscription-dialog.username")}
                className={cn(
                  "w-full pr-10",
                  username == "" &&
                    open &&
                    "border-2 border-destructive focus-visible:ring-destructive focus-visible:border-destructive",
                )}
              />
            </div>
          </div>

          <div className="grid grid-cols-4 items-center gap-4">
            <Label className="text-right">
              {t("subscription-dialog.password")}
            </Label>
            <div className="flex items-center col-span-3">
              <Input
                type={visible ? "text" : "password"}
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={t("subscription-dialog.password")}
                className={cn(
                  "w-full pr-10",
                  password == "" &&
                    open &&
                    "border-2 border-destructive focus-visible:ring-destructive focus-visible:border-destructive",
                )}
              />
            </div>
            <Button
              type="button"
              variant="ghostNoHover"
              size="icon"
              className={cn(
                "absolute right-6",
                password == "" && open && "absolute right-14",
              )}
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

      <ConfirmationDialog
        open={showLeaveConfirm}
        onOpenChange={setShowLeaveConfirm}
        dialogType="leave"
        action={() => {
          onOpenChange(false);
        }}
      />
    </>
  );
}
