"use client";

import { useEffect, useRef } from "react";

/**
 * The Aether-Flow particle network, reworked as a transparent background layer
 * (clearRect each frame so the page's dark gradient shows through). Purple nodes,
 * mouse-reactive links. Honors prefers-reduced-motion.
 */
export function ParticleField({ className = "" }: { className?: string }) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let raf = 0;
    let particles: Particle[] = [];
    const mouse: { x: number | null; y: number | null; radius: number } = {
      x: null,
      y: null,
      radius: 170,
    };

    const parent = canvas.parentElement;
    const dims = () => ({
      w: parent?.clientWidth ?? window.innerWidth,
      h: parent?.clientHeight ?? window.innerHeight,
    });

    class Particle {
      constructor(
        public x: number,
        public y: number,
        public dx: number,
        public dy: number,
        public size: number,
      ) {}

      draw() {
        ctx!.beginPath();
        ctx!.arc(this.x, this.y, this.size, 0, Math.PI * 2, false);
        ctx!.fillStyle = "rgba(191, 128, 255, 0.85)";
        ctx!.fill();
      }

      update() {
        if (this.x > canvas!.width || this.x < 0) this.dx = -this.dx;
        if (this.y > canvas!.height || this.y < 0) this.dy = -this.dy;

        if (mouse.x !== null && mouse.y !== null) {
          const ddx = mouse.x - this.x;
          const ddy = mouse.y - this.y;
          const dist = Math.sqrt(ddx * ddx + ddy * ddy);
          if (dist < mouse.radius + this.size) {
            const force = (mouse.radius - dist) / mouse.radius;
            this.x -= (ddx / dist) * force * 4;
            this.y -= (ddy / dist) * force * 4;
          }
        }
        this.x += this.dx;
        this.y += this.dy;
        this.draw();
      }
    }

    function init() {
      const { w, h } = dims();
      particles = [];
      const count = Math.min((w * h) / 11000, 140);
      for (let i = 0; i < count; i++) {
        const size = Math.random() * 1.8 + 1;
        particles.push(
          new Particle(
            Math.random() * w,
            Math.random() * h,
            Math.random() * 0.4 - 0.2,
            Math.random() * 0.4 - 0.2,
            size,
          ),
        );
      }
    }

    function connect() {
      const maxDist = (canvas!.width / 8) * (canvas!.height / 8);
      for (let a = 0; a < particles.length; a++) {
        for (let b = a; b < particles.length; b++) {
          const dx = particles[a].x - particles[b].x;
          const dy = particles[a].y - particles[b].y;
          const distance = dx * dx + dy * dy;
          if (distance < maxDist) {
            const opacity = 1 - distance / 18000;
            const mdx = particles[a].x - (mouse.x ?? -9999);
            const mdy = particles[a].y - (mouse.y ?? -9999);
            const near = Math.sqrt(mdx * mdx + mdy * mdy) < mouse.radius;
            ctx!.strokeStyle = near
              ? `rgba(226, 209, 255, ${opacity})`
              : `rgba(168, 120, 240, ${opacity * 0.55})`;
            ctx!.lineWidth = 1;
            ctx!.beginPath();
            ctx!.moveTo(particles[a].x, particles[a].y);
            ctx!.lineTo(particles[b].x, particles[b].y);
            ctx!.stroke();
          }
        }
      }
    }

    function frame() {
      raf = requestAnimationFrame(frame);
      ctx!.clearRect(0, 0, canvas!.width, canvas!.height);
      for (const p of particles) p.update();
      connect();
    }

    const resize = () => {
      const { w, h } = dims();
      canvas.width = w;
      canvas.height = h;
      init();
    };

    const onMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
    };
    const onLeave = () => {
      mouse.x = null;
      mouse.y = null;
    };

    resize();
    window.addEventListener("resize", resize);
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseout", onLeave);

    if (reduced) {
      // Draw a single static frame; no animation loop.
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (const p of particles) p.draw();
      connect();
    } else {
      frame();
    }

    return () => {
      window.removeEventListener("resize", resize);
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseout", onLeave);
      cancelAnimationFrame(raf);
    };
  }, []);

  return <canvas ref={ref} aria-hidden className={className} />;
}
