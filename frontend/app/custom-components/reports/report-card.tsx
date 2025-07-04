import type { ReportOverview } from "../../../types/model";
import { formatDate } from "~/lib/utils";
import { Button } from "~/components/ui/button";
import { Download, File } from "lucide-react";
import { useQuery } from "../../../types/api";
import { ErrorPage } from "~/pages/error/error";
import React from "react";
import { getReport } from "~/pages/reports/reports-dummy-data";

interface ReportCardProps {
  report: ReportOverview;
}

export function ReportCard({ report }: ReportCardProps) {
  // const {
  //   data: fullReport,
  //   error,
  // } = useQuery("/api/v1/reports/{report_id}", { params: { path: { report_id: report.id } } });
  const fullReport = getReport("550e8400-e29b-41d4-a716-446655440001");

  if (!fullReport) {
    return <ErrorPage />;
  }

  return (
    <div className="bg-gray-100 rounded-lg flex items-center justify-between px-2 py-1">
      <div className={"flex gap-2 items-center"}>
        <File className="w-5 h-5" />
        <p className={"font-semibold"}>{formatDate(report.created_at)}</p>
      </div>
      {fullReport.s3_url && (
        <a href={fullReport.s3_url} download>
          <Button variant={"ghost"} asChild>
            <Download />
          </Button>
        </a>
      )}
    </div>
  );
}
