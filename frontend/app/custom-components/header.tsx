import { Settings, User } from "lucide-react";
import { Button } from "~/components/ui/button";
import { Link } from "react-router";

export default function Header() {
  return (
    <div className="p-4 w-full grid grid-cols-13 items-center gap-4">
      <div className="col-span-3">
        <img src="/MediaMind_Logo.svg" alt="MediaMind_Logo" width="200" />
      </div>
      <div className="col-span-10 flex justify-end gap-2">
        <Button variant="outline">
          <User className="mr-2" />
          Login
        </Button>
        <Link to="/admin">
          <Button variant="outline">
            <Settings />
          </Button>
        </Link>
      </div>
    </div>
  );
}
