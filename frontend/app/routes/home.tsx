import { Welcome } from "../pages/welcome/welcome";
import type { MetaArgs } from "react-router";

export function meta({}: MetaArgs) {
  return [
    { title: "MediaMind | Landingpage" },
    { name: "description", content: "Welcome to MediaMind!" },
  ];
}

export default function Home() {
  return <Welcome />;
}
