export function shuffle<T>(array: T[]): T[] {
  const copy = [...array];
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

export function sample<T>(array: T[], count: number): T[] {
  if (count > array.length) {
    throw new Error('Sample size cannot exceed array length');
  }
  return shuffle(array).slice(0, count);
}
