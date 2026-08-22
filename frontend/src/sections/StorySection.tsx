import { motion } from "framer-motion";
import type { ReactNode } from "react";

interface StorySectionProps {
  index: string;
  line: string;
  title: string;
  body: string;
  visual: ReactNode;
  reverse?: boolean;
}

export default function StorySection({ index, line, title, body, visual, reverse }: StorySectionProps) {
  return (
    <section className="relative border-t border-hairline-soft px-5 py-20 md:px-10 md:py-28">
      <div
        className={`mx-auto flex max-w-5xl flex-col items-center gap-10 md:gap-16 ${
          reverse ? "md:flex-row-reverse" : "md:flex-row"
        }`}
      >
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-15% 0px" }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
          className="w-full md:w-[42%]"
        >
          <span className="label-eyebrow">{index}</span>
          <h2 className="mt-3 font-display text-3xl italic text-ivory md:text-4xl">{line}</h2>
          <h3 className="mt-4 text-sm font-medium uppercase tracking-wide text-ivory-dim">{title}</h3>
          <p className="mt-3 max-w-sm text-sm leading-relaxed text-mute">{body}</p>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-15% 0px" }}
          transition={{ duration: 0.7, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          className="w-full md:w-[58%]"
        >
          {visual}
        </motion.div>
      </div>
    </section>
  );
}
