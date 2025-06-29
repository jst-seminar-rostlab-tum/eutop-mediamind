import { LogOut, OctagonAlert, Trash2 } from "lucide-react";
import type { Dispatch, SetStateAction } from "react";
import { useTranslation } from "react-i18next";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "~/components/ui/alert-dialog";

interface ConfirmationDialogProps {
  open: boolean;
  onOpenChange: Dispatch<SetStateAction<boolean>>;
  dialogType: string;
  action: () => void;
}

export function ConfirmationDialog({
  open,
  onOpenChange,
  dialogType,
  action,
}: ConfirmationDialogProps) {
  const { t } = useTranslation();

  let description;

  if (dialogType == "delete") {
    description = t("confirmation_dialog.delete_text");
  } else if (dialogType == "leave") {
    description = t("confirmation_dialog.leave_text");
  } else {
    description = t("confirmation_dialog.unsaved_text"); //maybe not needed anymore
  }

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle className="flex items-center">
            <OctagonAlert size={20} className="text-red-500 mr-2" />
            {t("confirmation_dialog.title")}
          </AlertDialogTitle>
          <AlertDialogDescription>{description}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>{t("Back")}</AlertDialogCancel>
          <AlertDialogAction
            className="bg-destructive text-white shadow-xs hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60"
            onClick={action}
          >
            {dialogType == "delete" ? (
              <>
                <Trash2 />
                {t("Delete")}
              </>
            ) : (
              <>
                <LogOut className="text-white" />
                {t("Leave")}
              </>
            )}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
