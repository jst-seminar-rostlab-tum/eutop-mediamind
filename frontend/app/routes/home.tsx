import { Admin } from "../pages/admin/admin";

export function meta() {
  return [
    { title: "MediaMind | Landingpage" },
    { name: "description", content: "Welcome to MediaMind!" },
  ];
}

export default function Home() {
  return <Admin />;
}
