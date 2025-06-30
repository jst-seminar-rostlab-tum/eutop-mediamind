import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "~/components/ui/dialog";
import { Input } from "~/components/ui/input";
import { Button } from "~/components/ui/button";
import React, { useEffect, useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import type { Subscription } from "../types";
import { useTranslation } from "react-i18next";
import { ConfirmationDialog } from "~/custom-components/confirmation-dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "~/components/ui/form";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

const FormSchema = z.object({
  name: z
    .string()
    .min(1, { message: "Name is required." })
    .max(20, { message: "Max length is 20 characters." })
    .regex(/^[a-zA-Z0-9]+$/, {
      message: "Only letters and numbers are allowed.",
    }),

  url: z
    .string()
    .url({ message: "Must be a valid URL (e.g., https://example.com)" }),

  username: z
    .string()
    .min(2, { message: "Username must be at least 2 characters." })
    .max(30, { message: "Username must be at most 30 characters." })
    .regex(/^[a-zA-Z0-9_.-]+$/, {
      message:
        "Username may only contain letters, numbers, dots, dashes, or underscores.",
    }),

  password: z
    .string()
    .min(8, { message: "Password must be at least 8 characters." })
    .max(50, { message: "Password must be at most 50 characters." })
    .regex(/[a-z]/, { message: "Password must include a lowercase letter." })
    .regex(/[A-Z]/, { message: "Password must include an uppercase letter." })
    .regex(/[0-9]/, { message: "Password must include a number." })
    .regex(/[\W_]/, { message: "Password must include a special character." }),
});

type FormValues = z.infer<typeof FormSchema>;

type Props = {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  isEdit: boolean;
  onSave: (data: FormValues) => void;
  initialSub?: Subscription;
};

export function SubscriptionDialog({
  open,
  onOpenChange,
  isEdit,
  onSave,
  initialSub,
}: Props) {
  const [visible, setVisible] = useState(false);
  const [showLeaveConfirm, setShowLeaveConfirm] = React.useState(false);

  const { t } = useTranslation();

  const form = useForm<FormValues>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      name: initialSub ? initialSub.name : "",
      url: initialSub ? initialSub.url : "",
      username: initialSub ? initialSub.username : "",
      password: initialSub ? initialSub.password : "",
    },
  });

  useEffect(() => {
    form.reset({
      name: initialSub ? initialSub.name : "",
      url: initialSub ? initialSub.url : "",
      username: initialSub ? initialSub.username : "",
      password: initialSub ? initialSub.password : "",
    });
  }, [initialSub, open]);

  return (
    <>
      <Dialog
        open={open}
        onOpenChange={(isOpen) => {
          let subChanged = false;
          if (initialSub) {
            subChanged =
              form.getValues("name") !== initialSub.name ||
              form.getValues("url") !== initialSub.url ||
              form.getValues("username") !== initialSub.username ||
              form.getValues("password") !== initialSub.password;
          }
          if (!isOpen && subChanged) {
            setShowLeaveConfirm(true); // show AlertDialog instead
          } else {
            onOpenChange(isOpen); // normal open/close
          }
        }}
      >
        <DialogContent className="min-w-[400px]">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSave)} className="space-y-4">
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

              <div className="mx-4">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem className="grid grid-cols-4 items-center gap-x-4">
                      <FormLabel className="col-span-1 flex justify-end">
                        {t("subscription-dialog.Name")}
                      </FormLabel>
                      <FormControl className="col-span-3">
                        <Input
                          placeholder={t("subscription-dialog.Name")}
                          {...field}
                        />
                      </FormControl>
                      <FormMessage className="col-span-3 col-start-2" />
                    </FormItem>
                  )}
                />
              </div>

              <div className="mx-4">
                <FormField
                  control={form.control}
                  name="url"
                  render={({ field }) => (
                    <FormItem className="grid grid-cols-4 items-center gap-4">
                      <FormLabel className="col-span-1 flex justify-end">
                        {t("subscription-dialog.URL")}
                      </FormLabel>
                      <FormControl className="col-span-3">
                        <Input
                          placeholder={t("subscription-dialog.URL")}
                          {...field}
                        />
                      </FormControl>
                      <FormMessage className="col-span-3 col-start-2" />
                    </FormItem>
                  )}
                />
              </div>

              <div className="mx-4">
                <FormField
                  control={form.control}
                  name="username"
                  render={({ field }) => (
                    <FormItem className="grid grid-cols-4 items-center gap-4">
                      <FormLabel className="col-span-1 flex justify-end">
                        {t("subscription-dialog.Username")}
                      </FormLabel>
                      <FormControl className="col-span-3">
                        <Input
                          placeholder={t("subscription-dialog.Username")}
                          {...field}
                        />
                      </FormControl>
                      <FormMessage className="col-span-3 col-start-2" />
                    </FormItem>
                  )}
                />
              </div>

              <div className="mx-4">
                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem className="grid grid-cols-4 gap-4">
                      <FormLabel className="col-span-1 flex justify-end">
                        {t("subscription-dialog.Password")}
                      </FormLabel>
                      <FormControl className="col-span-3">
                        <div className="relative">
                          <Input
                            type={visible ? "text" : "password"}
                            placeholder={t("subscription-dialog.Password")}
                            className="pr-10" // add padding so text doesn't collide with button
                            {...field}
                          />
                          <Button
                            type="button"
                            variant="ghostNoHover"
                            size="icon"
                            className="absolute right-2 top-1/2 -translate-y-1/2"
                            onClick={() => setVisible((v) => !v)}
                          >
                            {visible ? (
                              <EyeOff className="h-4 w-4 " />
                            ) : (
                              <Eye className="h-4 w-4" />
                            )}
                          </Button>
                        </div>
                      </FormControl>
                      <FormMessage className="col-span-3 col-start-2" />
                    </FormItem>
                  )}
                />
              </div>

              <DialogFooter>
                <Button type="submit">{t("save_changes")}</Button>
              </DialogFooter>
            </form>
          </Form>
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
