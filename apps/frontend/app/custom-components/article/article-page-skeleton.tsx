import React from "react";
import { Skeleton } from "~/components/ui/skeleton";
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "~/components/ui/accordion";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "~/components/ui/breadcrumb";
import { Calendar, FileClock, User } from "lucide-react";
import Layout from "~/custom-components/layout";

export function ArticlePageSkeleton() {
  return (
    <Layout>
      <div className="flex gap-15">
        <div className="w-2/3 space-y-8">
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbLink>
                  <Skeleton className="h-4 w-16" />
                </BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbLink>
                  <Skeleton className="h-4 w-24" />
                </BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbPage>
                  <Skeleton className="h-4 w-32" />
                </BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>

          <div className="space-y-6">
            <Skeleton className="h-9 w-3/4" />

            <div className="flex text-gray-500 text-sm">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-gray-300" />
                <Skeleton className="h-4 w-20" />
              </div>
              <span className="mx-4 text-gray-300">•</span>
              <div className="flex items-center gap-2">
                <User className="w-4 h-4 text-gray-300" />
                <Skeleton className="h-4 w-24" />
              </div>
              <span className="mx-4 text-gray-300">•</span>
              <div className="flex items-center gap-2">
                <FileClock className="w-4 h-4 text-gray-300" />
                <Skeleton className="h-4 w-12" />
              </div>
            </div>

            <article className="prose max-w-none space-y-6">
              <div className="space-y-3">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-5/6" />
                <Skeleton className="h-4 w-full" />
              </div>

              <Skeleton className="h-7 w-2/5 mt-8" />

              <div className="space-y-3">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-4/5" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-5/6" />
              </div>

              <div className="border-l-4 border-gray-200 pl-4 my-6">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-4/5" />
                <Skeleton className="h-4 w-3/4" />
              </div>

              <Skeleton className="h-7 w-1/2 mt-8" />

              <div className="space-y-3">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-2/3" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-5/6" />
              </div>
            </article>
          </div>
        </div>

        <div className="w-1/3">
          <div className="space-y-6">
            <Skeleton className="h-9 w-40 mr-2" />

            <div className="rounded-3xl pl-4 pr-4 border">
              <Accordion
                type="single"
                collapsible
                className="w-full"
                defaultValue="summary"
              >
                <AccordionItem value="summary">
                  <AccordionTrigger>
                    <Skeleton className="h-5 w-16" />
                  </AccordionTrigger>
                  <AccordionContent className="pb-4">
                    <div className="space-y-2">
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-3/4" />
                    </div>
                  </AccordionContent>
                </AccordionItem>
              </Accordion>
            </div>

            <div className="rounded-3xl border p-4 space-y-2">
              <Skeleton className="h-5 w-20" />
              <Skeleton className="h-4 w-full" />

              {[1, 2, 3].map((index) => (
                <div
                  key={index}
                  className="space-y-1 bg-gray-100 p-2 rounded-2xl h-20"
                ></div>
              ))}
            </div>

            <div className="space-y-4">
              <Skeleton className="h-6 w-32" />
              <div className="space-y-2">
                {[1, 2, 3, 4, 5].map((index) => (
                  <div
                    key={index}
                    className="flex justify-between py-2 border-b"
                  >
                    <Skeleton className="h-4 w-20" />
                    <Skeleton className="h-4 w-24" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
