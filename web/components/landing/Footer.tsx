import { Logo } from "@/components/shared/Logo";

const COLS = [
  {
    title: "Product",
    links: [
      { label: "How it works", href: "#how" },
      { label: "Family protection", href: "#family" },
      { label: "Live scam map", href: "#map" },
      { label: "Recent activity", href: "#activity" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About", href: "#top" },
      { label: "Careers", href: "#top" },
      { label: "Press", href: "#top" },
      { label: "Contact", href: "#top" },
    ],
  },
  {
    title: "Trust",
    links: [
      { label: "Privacy", href: "#top" },
      { label: "Security", href: "#top" },
      { label: "Report a scam", href: "#top" },
      { label: "1930 helpline", href: "tel:1930" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="border-t border-line bg-offwhite px-5 py-14">
      <div className="mx-auto grid max-w-6xl gap-10 md:grid-cols-[1.4fr_repeat(3,1fr)]">
        <div>
          <Logo />
          <p className="mt-4 max-w-xs text-[14px] leading-relaxed text-ink-soft">
            Security for humans, not cybersecurity experts. Before you click, pay, or trust anything, ask ScamShield.
          </p>
        </div>
        {COLS.map((c) => (
          <div key={c.title}>
            <p className="text-[13px] font-semibold text-ink">{c.title}</p>
            <ul className="mt-4 space-y-2.5">
              {c.links.map((l) => (
                <li key={l.label}>
                  <a href={l.href} className="text-[14px] text-ink-soft transition-colors hover:text-trust-600">
                    {l.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="mx-auto mt-12 flex max-w-6xl flex-col items-center justify-between gap-3 border-t border-line pt-6 text-[13px] text-ink-faint sm:flex-row">
        <p>© {new Date().getFullYear()} ScamShield AI. Made with care in India.</p>
        <p>Not affiliated with any bank. In an emergency, call the cyber helpline 1930.</p>
      </div>
    </footer>
  );
}
