import type { ReportOverview } from "../../../types/model";
import { getDateComponents } from "~/lib/utils";
import { Button } from "~/components/ui/button";
import { Calendar, Download } from "lucide-react";
import React from "react";
import { useQuery } from "types/api";
import { RoleBadge } from "~/custom-components/dashboard/role-badge";
import { useTranslation } from "react-i18next";

interface ReportCardProps {
  report: ReportOverview;
}

export function ReportCard({ report }: ReportCardProps) {
  const { data: fullReport, error } = useQuery("/api/v1/reports/{report_id}", {
    params: { path: { report_id: report.id } },
  });
  const dateComponents = getDateComponents(report.created_at);

  const { t } = useTranslation();
  if (!fullReport || error) {
    return <div></div>;
  }

  return (
    <div className="shadow-lg border-2 rounded-lg p-4 h-40 w-50 space-y-1 flex flex-col justify-between">
      <div className={"flex items-center gap-2"}>
        <Calendar className="w-6 h-6" />
        <div className={"flex items-baseline space-x-2"}>
          <span className={"font-semibold text-2xl"}>{dateComponents.day}</span>
          <div className={"flex space-x-1"}>
            <span>{dateComponents.month}</span>
            <span>{dateComponents.year}</span>
          </div>
        </div>
      </div>
      <div className={"flex gap-2 items-center"}>
        <div>
          {fullReport.language === "en" ? (
            <RoleBadge variant={"en"} />
          ) : (
            <RoleBadge variant={"de"} />
          )}
        </div>
        <div>
          {fullReport.time_slot === "morning" ? (
            <RoleBadge variant={"morning"} />
          ) : fullReport.time_slot === "evening" ? (
            <RoleBadge variant={"evening"} />
          ) : (
            <RoleBadge variant={"afternoon"} />
          )}
        </div>
      </div>

      {fullReport.s3_url ? (
        <Button asChild>
          <a href={fullReport.s3_url} download>
            {t("reports.download")}
            <Download />
          </a>
        </Button>
      ) : (
        <Button disabled>
          {t("reports.download_unavailable")}
          <Download />
        </Button>
      )}
    </div>
  );
}
