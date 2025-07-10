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
import React, { useEffect, useMemo, useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import type { Subscription } from "types/model";
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
import { useQuery } from "types/api";
import { cloneDeep, isEqual } from "lodash-es";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import type { TFunction } from "i18next";
import { Skeleton } from "~/components/ui/skeleton";

const createFormSchema = (t: TFunction) =>
  z.object({
    id: z.string(),
    name: z
      .string()
      .min(1, { message: t("subscription-dialog.name_required") })
      .max(20, { message: t("subscription-dialog.name_length") })
      .regex(/^[a-zA-Z0-9]+$/, {
        message: t("subscription-dialog.name_regex"),
      }),
    url: z.string().url({ message: t("subscription-dialog.url_valid") }),
    paywall: z.boolean(),
    username: z.string(),
    password: z.string(),
  });

export type FormValues = z.infer<ReturnType<typeof createFormSchema>>;

type Props = {
  open: boolean;
  onOpenChange: (value: boolean) => void;
  isEdit: boolean;
  sub: Subscription | null;
  onSave: (data: FormValues) => void;
};

export function SubscriptionDialog({
  open,
  onOpenChange,
  isEdit,
  sub,
  onSave,
}: Props) {
  const { t } = useTranslation();
  const formSchema = useMemo(() => createFormSchema(t), [t]);

  const [visible, setVisible] = useState(false);
  const [showLeaveConfirm, setShowLeaveConfirm] = React.useState(false);

  const initialSub = {
    id: "",
    name: "",
    domain: "",
    paywall: false,
    username: "",
  };

  // Get subscription if editing
  const {
    data: fetchedSubData,
    isLoading: subLoading,
    mutate: mutateFetchedSubData,
  } = useQuery(
    "/api/v1/subscriptions/{subscription_id}",
    sub
      ? { params: { path: { subscription_id: sub.id } } }
      : {
          params: { path: { subscription_id: "" } },
        },
  );

  const [loadingFreshSub, setLoadingFreshSub] = useState(false);

  useEffect(() => {
    const revalidate = async () => {
      if (open && isEdit && sub?.id && mutateFetchedSubData) {
        setLoadingFreshSub(true);
        await mutateFetchedSubData();
        setLoadingFreshSub(false);
      }
    };
    revalidate();
  }, [open, isEdit, sub?.id, mutateFetchedSubData]);

  console.log(fetchedSubData);

  const subData = useMemo(() => {
    return cloneDeep(isEdit && fetchedSubData ? fetchedSubData : initialSub);
  }, [isEdit, fetchedSubData]);

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      id: subData ? subData.id : "", // info: id is part of form but can't be edited in the dialog
      name: subData ? subData.name : "",
      url: subData ? subData.domain : "",
      paywall: subData ? subData.paywall : false,
      username: subData ? subData.username : "",
      password: "",
    },
  });

  useEffect(() => {
    form.reset({
      id: subData ? subData.id : "", // info: id is part of form but can't be edited in the dialog
      name: subData ? subData.name : "",
      url: subData ? subData.domain : "",
      paywall: subData ? subData.paywall : false,
      username: subData ? subData.username : "",
      password: "",
    });
  }, [subData, open]);

  const checkEqual = (isEdit: boolean) => {
    const base = isEdit ? subData : initialSub;

    const updated = {
      ...base, // just id
      // get current name input
      name: form.getValues().name,
      domain: form.getValues().url,
      paywall: form.getValues().paywall,
      username: form.getValues().username,
    };

    return isEqual(updated, base);
  };

  const paywall = form.watch("paywall");

  return (
    <>
      <Dialog
        open={open}
        onOpenChange={(isOpen) => {
          if (!checkEqual(isEdit)) {
            setShowLeaveConfirm(true); // if changes, show AlertDialog
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
                    <FormItem className="grid grid-cols-4 items-center gap-x-4 gap-y-1">
                      <FormLabel className="col-span-1 flex justify-end">
                        {t("subscription-dialog.Name")}
                      </FormLabel>
                      <FormControl className="col-span-3">
                        {loadingFreshSub || subLoading ? (
                          <Skeleton className="h-9 w-full rounded-md" />
                        ) : (
                          <Input
                            placeholder={t("subscription-dialog.Name")}
                            {...field}
                          />
                        )}
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
                    <FormItem className="grid grid-cols-4 items-center gap-x-4 gap-y-1">
                      <FormLabel className="col-span-1 flex justify-end">
                        {t("subscription-dialog.URL")}
                      </FormLabel>
                      <FormControl className="col-span-3">
                        {loadingFreshSub || subLoading ? (
                          <Skeleton className="h-9 w-full rounded-md" />
                        ) : (
                          <Input
                            placeholder={t("subscription-dialog.URL")}
                            {...field}
                          />
                        )}
                      </FormControl>
                      <FormMessage className="col-span-3 col-start-2" />
                    </FormItem>
                  )}
                />
              </div>

              <div className="mx-4">
                <FormField<FormValues, "paywall">
                  control={form.control}
                  name="paywall"
                  render={({ field }) => (
                    <FormItem className="grid grid-cols-4 items-center gap-x-4 gap-y-1">
                      <FormLabel className="col-span-1 flex justify-end">
                        {t("subscription-dialog.Paywall")}
                      </FormLabel>
                      <FormControl className="col-span-3">
                        {loadingFreshSub || subLoading ? (
                          <Skeleton className="h-9 w-[30%] rounded-md" />
                        ) : (
                          <Select
                            value={field.value ? "true" : "false"}
                            onValueChange={(value) =>
                              field.onChange(value === "true")
                            }
                          >
                            <SelectTrigger className="w-full">
                              <SelectValue
                                placeholder={t("subscription-dialog.Paywall")}
                              />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="true">{t("Yes")}</SelectItem>
                              <SelectItem value="false">{t("No")}</SelectItem>
                            </SelectContent>
                          </Select>
                        )}
                      </FormControl>
                      <FormMessage className="col-span-3 col-start-2" />
                    </FormItem>
                  )}
                />
              </div>

              {paywall && (
                <>
                  <div className="mx-4">
                    <FormField
                      control={form.control}
                      name="username"
                      render={({ field }) => (
                        <FormItem className="grid grid-cols-4 items-center gap-x-4 gap-y-1">
                          <FormLabel className="col-span-1 flex justify-end">
                            {t("subscription-dialog.Username")}
                          </FormLabel>
                          <FormControl className="col-span-3">
                            {loadingFreshSub || subLoading ? (
                              <Skeleton className="h-9 w-full rounded-md" />
                            ) : (
                              <Input
                                placeholder={t("subscription-dialog.Username")}
                                {...field}
                              />
                            )}
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
                        <FormItem className="grid grid-cols-4 gap-x-4 gap-y-1">
                          <FormLabel className="col-span-1 flex justify-end">
                            {t("subscription-dialog.Password")}
                          </FormLabel>
                          <FormControl className="col-span-3">
                            {loadingFreshSub || subLoading ? (
                              <Skeleton className="h-9 w-full rounded-md" />
                            ) : (
                              <div className="relative">
                                <Input
                                  type={visible ? "text" : "password"}
                                  placeholder={t(
                                    "subscription-dialog.Password",
                                  )}
                                  className="pr-10"
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
                            )}
                          </FormControl>
                          <FormMessage className="col-span-3 col-start-2" />
                        </FormItem>
                      )}
                    />
                  </div>
                </>
              )}

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
