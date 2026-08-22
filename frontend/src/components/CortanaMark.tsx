// The CORTANA mark: a sparse contour of nodes and connecting lines that
// reads simultaneously as a faint holographic presence (hero) and as the
// fusion network diagram (Model Intelligence). This shared linework is
// the visual system's signature — everywhere the "AI" appears, it is
// built from the same nodes-and-thin-lines vocabulary, never a literal
// rendered face.

interface CortanaMarkProps {
  className?: string;
  variant?: "presence" | "compact";
  animate?: boolean;
}

export default function CortanaMark({
  className = "",
  variant = "presence",
  animate = true,
}: CortanaMarkProps) {
  const nodes: [number, number, number][] = [
    [220, 90, 2.4], // crown
    [175, 130, 1.6],
    [265, 130, 1.6],
    [150, 210, 2.2], // brow L
    [290, 210, 2.2], // brow R
    [190, 235, 3.2], // eye L
    [250, 235, 3.2], // eye R
    [220, 270, 1.4], // bridge
    [220, 320, 2.6], // nose base
    [175, 355, 1.8],
    [265, 355, 1.8],
    [220, 400, 2.2], // mouth center
    [140, 300, 1.4],
    [300, 300, 1.4],
    [120, 380, 1.2],
    [320, 380, 1.2],
    [220, 460, 1.8], // jaw
  ];

  const edges: [number, number][] = [
    [0, 1], [0, 2], [1, 3], [2, 4], [3, 5], [4, 6], [5, 7], [6, 7],
    [7, 8], [8, 9], [8, 10], [9, 11], [10, 11], [3, 12], [4, 13],
    [12, 14], [13, 15], [9, 14], [10, 15], [11, 16], [14, 16], [15, 16],
  ];

  return (
    <svg
      viewBox="0 0 440 520"
      className={className}
      role="img"
      aria-label="CORTANA holographic intelligence mark"
    >
      <defs>
        <radialGradient id="cortana-glow" cx="50%" cy="42%" r="60%">
          <stop offset="0%" stopColor="var(--color-intel)" stopOpacity="0.16" />
          <stop offset="100%" stopColor="var(--color-intel)" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="cortana-line" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="var(--color-intel)" stopOpacity="0.85" />
          <stop offset="100%" stopColor="var(--color-ivory)" stopOpacity="0.25" />
        </linearGradient>
      </defs>

      {variant === "presence" && (
        <circle cx="220" cy="240" r="230" fill="url(#cortana-glow)" />
      )}

      {edges.map(([a, b], i) => (
        <line
          key={i}
          x1={nodes[a][0]}
          y1={nodes[a][1]}
          x2={nodes[b][0]}
          y2={nodes[b][1]}
          stroke="url(#cortana-line)"
          strokeWidth="0.6"
          opacity={0.5}
        >
          {animate && (
            <animate
              attributeName="opacity"
              values="0.25;0.55;0.25"
              dur={`${6 + (i % 5)}s`}
              repeatCount="indefinite"
            />
          )}
        </line>
      ))}

      {nodes.map(([x, y, r], i) => (
        <circle key={i} cx={x} cy={y} r={r} fill="var(--color-ivory)" opacity="0.75">
          {animate && (
            <animate
              attributeName="opacity"
              values="0.4;0.9;0.4"
              dur={`${5 + (i % 4)}s`}
              repeatCount="indefinite"
            />
          )}
        </circle>
      ))}

      {/* faint scan line */}
      <line x1="60" y1="240" x2="380" y2="240" stroke="var(--color-intel)" strokeWidth="0.4" opacity="0.2" />
    </svg>
  );
}
