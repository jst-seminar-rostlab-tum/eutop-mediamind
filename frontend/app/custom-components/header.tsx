import { User } from "lucide-react";
import { Button } from "~/components/ui/button";

export default function Header() {
  return (
    <div className="p-4 w-full flex justify-between items-center">
      <img src="/MediaMind_Logo.svg" alt="MediaMind_Logo" width={"180px"} />
      <Button variant={"white"}>
        <User />
        Login
      </Button>
    </div>
  );
}
