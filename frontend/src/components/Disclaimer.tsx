import { Badge } from "@/components/ui";

export default function Disclaimer() {
  return (
    <div className="mx-auto max-w-[1400px] px-5 py-4">
      <div className="flex items-start gap-2 rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-[11px] leading-relaxed text-slate-500">
        <svg className="mt-0.5 h-3.5 w-3.5 shrink-0 text-slate-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden>
          <path
            fillRule="evenodd"
            d="M18 10A8 8 0 11-2 10a8 8 0 0112 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.732 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.268 9H9z"
            clipRule="evenodd"
          />
        </svg>
        <p>
          <strong className="text-slate-600">Product limitation:</strong> RakshaAI is a prototype decision-support
          system. Risk scores are model-generated estimates and should not replace official forecasts, warnings, or
          emergency-management instructions. Location and infrastructure data shown is demo/simulation data labelled{" "}
          <Badge tone="amber">DEMO DATA</Badge>.
        </p>
      </div>
    </div>
  );
}