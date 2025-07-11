import { ErrorPage } from "~/pages/error/error";

export function meta() {
  return [
    { title: "MediaMind | Error" },
    { name: "description", content: "Oohps! Something went wrong!" },
  ];
}

export default function Error() {
  return <ErrorPage />;
}
