import { AdminPage } from "../pages/admin/admin";

export function meta() {
  return [
    { title: "MediaMind | Admin Settings" },
    { name: "description", content: "Admin Settings" },
  ];
}

export default function Admin() {
  return <AdminPage />;
}
