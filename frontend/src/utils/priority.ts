export function computePriority(deadlineISO: string, confidence: number): number {
  const msPerDay = 1000 * 60 * 60 * 24;
  const now = new Date();
  const deadline = new Date(deadlineISO);
  const days = Math.max((deadline.getTime() - now.getTime()) / msPerDay, 0.01);
  return (1 / days) * (6 - confidence);
}
