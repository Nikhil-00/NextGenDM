import Link from "next/link";
import { Button } from "@/components/ui/button";
import { MessageSquare, Zap, Users, Link2, ArrowRight, CheckCircle } from "lucide-react";

const features = [
  {
    icon: MessageSquare,
    title: "Auto Reply to Comments",
    description: "When someone comments a keyword on your post, instantly send them a DM — no manual work.",
  },
  {
    icon: Zap,
    title: "DM Keyword Automation",
    description: "Respond to DMs automatically. Set keywords and let NextGen DM handle replies 24/7.",
  },
  {
    icon: Users,
    title: "Follow-to-Unlock",
    description: "Gate your content. Only send links or PDFs to users who already follow your account.",
  },
  {
    icon: Link2,
    title: "Send PDF & Download Links",
    description: "Deliver lead magnets, guides, and freebies automatically via Instagram DM.",
  },
];

const steps = [
  "Sign up for free",
  "Connect your Instagram Business account",
  "Create your first automation",
  "Watch messages send themselves",
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 lg:px-12 h-16 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary">
            <MessageSquare className="w-4 h-4 text-primary-foreground" />
          </div>
          <span className="font-bold text-lg">NextGen DM</span>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/login">
            <Button variant="ghost" size="sm">Log in</Button>
          </Link>
          <Link href="/signup">
            <Button size="sm">Get Started</Button>
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="flex flex-col items-center text-center px-6 pt-24 pb-20">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-primary/30 bg-primary/10 text-primary text-xs font-medium mb-6">
          <Zap className="w-3.5 h-3.5" />
          Instagram Automation Platform
        </div>
        <h1 className="text-4xl sm:text-6xl font-bold tracking-tight max-w-3xl leading-tight">
          Automate Your{" "}
          <span className="text-primary">Instagram DMs</span>{" "}
          on Autopilot
        </h1>
        <p className="text-muted-foreground text-lg mt-6 max-w-xl leading-relaxed">
          Turn comments into conversations. Deliver lead magnets automatically. Gate content behind follows.
          All using Meta's official APIs.
        </p>
        <div className="flex items-center gap-3 mt-8">
          <Link href="/signup">
            <Button size="lg" className="gap-2">
              Get Started Free <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
          <Link href="/login">
            <Button variant="outline" size="lg">Connect Instagram</Button>
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="px-6 lg:px-12 py-20">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-3">Everything you need to grow</h2>
          <p className="text-muted-foreground text-center mb-12">
            Powerful automations built on Meta's official APIs
          </p>
          <div className="grid sm:grid-cols-2 gap-6">
            {features.map(({ icon: Icon, title, description }) => (
              <div key={title} className="p-6 rounded-xl border border-border bg-card hover:border-primary/40 transition-colors">
                <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary/10 mb-4">
                  <Icon className="w-5 h-5 text-primary" />
                </div>
                <h3 className="font-semibold mb-2">{title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="px-6 lg:px-12 py-20 bg-card/50">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-3">Get started in minutes</h2>
          <p className="text-muted-foreground mb-10">No technical skills required</p>
          <div className="space-y-4 text-left">
            {steps.map((step, i) => (
              <div key={i} className="flex items-center gap-4 p-4 rounded-xl border border-border bg-card">
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground text-sm font-bold shrink-0">
                  {i + 1}
                </div>
                <span className="font-medium">{step}</span>
                <CheckCircle className="w-4 h-4 text-primary ml-auto shrink-0" />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 py-24 text-center">
        <h2 className="text-3xl font-bold mb-4">Ready to automate?</h2>
        <p className="text-muted-foreground mb-8">Join creators using NextGen DM to grow on Instagram.</p>
        <Link href="/signup">
          <Button size="lg" className="gap-2">
            Start for Free <ArrowRight className="w-4 h-4" />
          </Button>
        </Link>
      </section>

      {/* Footer */}
      <footer className="border-t border-border px-6 py-6 text-center text-sm text-muted-foreground">
        © 2026 NextGen DM — Built with Meta Official APIs
      </footer>
    </div>
  );
}
