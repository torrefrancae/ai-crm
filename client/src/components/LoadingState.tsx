export function LoadingState({ label = "Loading workspace..." }: { label?: string }) {
  return (
    <div className="loading">
      <div className="bar" />
      {label}
    </div>
  );
}
