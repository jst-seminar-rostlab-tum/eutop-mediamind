import {
  Dialog,
  DialogContent,
  DialogTrigger,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "~/components/ui/dialog";
import { Button } from "~/components/ui/button";
import { DataTableAddMail } from "~/custom-components/profile/edit/data-table-add-mail";

export function AddMailDialog() {
  return (
    <Dialog>
      <form>
        <DialogTrigger asChild>
          <Button variant="outline">Add</Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Add Mail</DialogTitle>
            <DialogDescription>
              Add a person to the press release mailing list.
            </DialogDescription>
          </DialogHeader>
          <DataTableAddMail name={"Mail"} dataArray={["abc@mail.com"]} />
        </DialogContent>
      </form>
    </Dialog>
  );
}
