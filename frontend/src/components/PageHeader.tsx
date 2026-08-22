import type { ReactNode } from "react";

interface PageHeaderProps {
  eyebrow: string;
  title: string;
  description?: string;
  actions?: ReactNode;
}

export default function PageHeader({ eyebrow, title, description, actions }: PageHeaderProps) {
  return (
    <div className="flex flex-col gap-4 border-b border-hairline px-5 py-6 md:flex-row md:items-end md:justify-between md:px-8">
      <div>
        <p className="label-eyebrow">{eyebrow}</p>
        <h1 className="mt-1 font-display text-2xl text-ivory md:text-3xl">{title}</h1>
        {description && <p className="mt-1 max-w-xl text-sm text-mute">{description}</p>}
      </div>
      {actions && <div className="shrink-0">{actions}</div>}
    </div>
  );
}
