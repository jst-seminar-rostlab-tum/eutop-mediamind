import { Welcome } from "~/pages/welcome/welcome";

export function meta() {
  return [
    { title: "MediaMind | Landingpage" },
    { name: "description", content: "Welcome to MediaMind!" },
  ];
}

export default function Home() {
  return <Welcome />;
}
